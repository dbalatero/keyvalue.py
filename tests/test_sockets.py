import socket
import threading
from contextlib import closing

from keyvalue.sockets import MAX_REQUEST_BYTES, TcpSocketServer, UnixSocketServer
from keyvalue.store import Store


class FakeConnection:
    def __init__(self, request: bytes):
        self.request = request
        self.response = b""

    def recv(self, size: int) -> bytes:
        chunk = self.request[:size]
        self.request = self.request[size:]
        return chunk

    def sendall(self, response: bytes) -> None:
        self.response += response


def test_unix_socket_server_create_socket_binds_unix_socket(tmp_path) -> None:
    socket_path = tmp_path / "keyvalue.sock"
    store = Store(tmp_path / "data")
    server = UnixSocketServer(socket_path=socket_path, store=store)

    with server._create_socket() as sock:
        assert sock.family == socket.AF_UNIX
        assert sock.type == socket.SOCK_STREAM
        assert socket_path.exists()


def test_unix_socket_server_create_socket_listens_for_connections(tmp_path) -> None:
    socket_path = tmp_path / "keyvalue.sock"
    store = Store(tmp_path / "data")
    server = UnixSocketServer(socket_path=socket_path, store=store)

    with server._create_socket():
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(socket_path))


def test_unix_socket_server_create_socket_removes_stale_socket_file(tmp_path) -> None:
    socket_path = tmp_path / "keyvalue.sock"
    store = Store(tmp_path / "data")
    server = UnixSocketServer(socket_path=socket_path, store=store)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as stale_server:
        stale_server.bind(str(socket_path))

    with server._create_socket() as sock:
        assert sock.family == socket.AF_UNIX
        assert socket_path.exists()


def test_tcp_socket_server_create_socket_binds_tcp_socket(tmp_path) -> None:
    store = Store(tmp_path / "data")
    server = TcpSocketServer(store=store, host="127.0.0.1", port=0)

    with server._create_socket() as sock:
        assert sock.family == socket.AF_INET
        assert sock.type == socket.SOCK_STREAM


def test_tcp_socket_server_create_socket_listens_for_connections(tmp_path) -> None:
    store = Store(tmp_path / "data")
    server = TcpSocketServer(store=store, host="127.0.0.1", port=0)

    with server._create_socket() as sock:
        host, port = sock.getsockname()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((host, port))


def test_unix_socket_server_accept_one_accepts_client_connection_and_handles_request(
    tmp_path,
) -> None:
    socket_path = tmp_path / "keyvalue.sock"
    store = Store(tmp_path / "data")
    server = UnixSocketServer(socket_path=socket_path, store=store)
    response = None

    def client_request() -> None:
        nonlocal response

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(socket_path))
            client.sendall(b'{"command":"set","key":"name","value":"Alice"}\n')
            response = client.recv(4096)

    with server._create_socket() as sock:
        client_thread = threading.Thread(target=client_request)
        client_thread.start()

        server._accept_one(sock)

        client_thread.join(timeout=1)

    assert response == b'{"ok":true}\n'
    assert store.get("name") == "Alice"
    assert not client_thread.is_alive()


def test_unix_socket_server_handle_connection_reads_request_and_writes_response(
    tmp_path,
) -> None:
    client, server = socket.socketpair()
    store = Store(tmp_path / "data")
    socket_server = UnixSocketServer(
        socket_path=tmp_path / "keyvalue.sock",
        store=store,
    )

    with closing(client), closing(server):
        client.sendall(b'{"command":"set","key":"name","value":"Alice"}\n')

        socket_server._handle_connection(server)

        assert client.recv(4096) == b'{"ok":true}\n'
        assert store.get("name") == "Alice"


def test_unix_socket_server_handle_connection_reads_request_larger_than_recv_size(
    tmp_path,
) -> None:
    store = Store(tmp_path / "data")
    socket_server = UnixSocketServer(
        socket_path=tmp_path / "keyvalue.sock",
        store=store,
    )
    value = "a" * 4097
    request = f'{{"command":"set","key":"large","value":"{value}"}}\n'.encode()
    conn = FakeConnection(request)

    socket_server._handle_connection(conn)

    assert conn.response == b'{"ok":true}\n'
    assert store.get("large") == value


def test_unix_socket_server_handle_connection_writes_error_for_request_over_limit(
    tmp_path,
) -> None:
    store = Store(tmp_path / "data")
    socket_server = UnixSocketServer(
        socket_path=tmp_path / "keyvalue.sock",
        store=store,
    )
    value = "a" * (MAX_REQUEST_BYTES + 1)
    request = f'{{"command":"set","key":"large","value":"{value}"}}\n'.encode()
    conn = FakeConnection(request)

    socket_server._handle_connection(conn)

    assert b'"ok":false' in conn.response
    assert b"request is too large" in conn.response


def test_unix_socket_server_handle_connection_writes_error_response_for_invalid_request(
    tmp_path,
) -> None:
    client, server = socket.socketpair()
    store = Store(tmp_path / "data")
    socket_server = UnixSocketServer(
        socket_path=tmp_path / "keyvalue.sock",
        store=store,
    )

    with closing(client), closing(server):
        client.sendall(b'{"command":"get","key":"Invalid"}\n')

        socket_server._handle_connection(server)

        response = client.recv(4096)
        assert b'"ok":false' in response
        assert b"invalid key" in response
