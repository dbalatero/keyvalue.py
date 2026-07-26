import socket
from contextlib import closing

from keyvalue.sockets import handle_connection
from keyvalue.store import Store


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
