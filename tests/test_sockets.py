import socket
import threading
from contextlib import closing

from keyvalue.sockets import accept_one, create_server_socket, handle_connection
from keyvalue.store import Store


def test_create_server_socket_binds_unix_socket(tmp_path) -> None:
    socket_path = tmp_path / "keyvalue.sock"

    with create_server_socket(socket_path) as server:
        assert server.family == socket.AF_UNIX
        assert server.type == socket.SOCK_STREAM
        assert socket_path.exists()


def test_create_server_socket_listens_for_connections(tmp_path) -> None:
    socket_path = tmp_path / "keyvalue.sock"

    with create_server_socket(socket_path):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(socket_path))


def test_create_server_socket_removes_stale_socket_file(tmp_path) -> None:
    socket_path = tmp_path / "keyvalue.sock"

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as stale_server:
        stale_server.bind(str(socket_path))

    with create_server_socket(socket_path) as server:
        assert server.family == socket.AF_UNIX
        assert socket_path.exists()


def test_accept_one_accepts_client_connection_and_handles_request(tmp_path) -> None:
    socket_path = tmp_path / "keyvalue.sock"
    store = Store(tmp_path / "data")
    response = None

    def client_request() -> None:
        nonlocal response

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(socket_path))
            client.sendall(b'{"command":"set","key":"name","value":"Alice"}\n')
            response = client.recv(4096)

    with create_server_socket(socket_path) as server:
        client_thread = threading.Thread(target=client_request)
        client_thread.start()

        accept_one(server, store)

        client_thread.join(timeout=1)

    assert response == b'{"ok":true}\n'
    assert store.get("name") == "Alice"
    assert not client_thread.is_alive()


def test_handle_connection_reads_request_and_writes_response(tmp_path) -> None:
    client, server = socket.socketpair()
    store = Store(tmp_path / "data")

    with closing(client), closing(server):
        client.sendall(b'{"command":"set","key":"name","value":"Alice"}\n')

        handle_connection(server, store)

        assert client.recv(4096) == b'{"ok":true}\n'
        assert store.get("name") == "Alice"


def test_handle_connection_writes_error_response_for_invalid_request(tmp_path) -> None:
    client, server = socket.socketpair()
    store = Store(tmp_path / "data")

    with closing(client), closing(server):
        client.sendall(b'{"command":"get","key":"Invalid"}\n')

        handle_connection(server, store)

        response = client.recv(4096)
        assert b'"ok":false' in response
        assert b"invalid key" in response
