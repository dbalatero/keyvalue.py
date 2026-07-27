import pytest

from keyvalue.client import Client, FifoTransport, SocketTransport
from server_helpers import (
    RunningServer,
    start_fifo_server,
    start_socket_server,
    stop_server,
)


def make_client(server: RunningServer) -> Client:
    transport = (
        SocketTransport(server.path)
        if server.mode == "socket"
        else FifoTransport(server.path)
    )
    return Client(transport)


@pytest.mark.parametrize(
    ("start_server",),
    [
        (start_socket_server,),
        (start_fifo_server,),
    ],
)
def test_server_process_handles_client_requests(tmp_path, start_server) -> None:
    server = start_server(tmp_path)
    client = make_client(server)

    try:
        client.set("name", "Alice")
        assert client.get("name") == "Alice"
        assert client.keys() == ["name"]

        client.set("foo", "bar")
        assert client.keys() == ["foo", "name"]

        client.delete("foo")
        assert client.keys() == ["name"]
        assert client.get("foo") is None

        client.set("name", "Jeff")
        assert client.get("name") == "Jeff"
    finally:
        stop_server(server.process)
