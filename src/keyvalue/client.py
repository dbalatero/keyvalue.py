import socket
from pathlib import Path

from keyvalue.fifo import fifo_paths
from keyvalue.requests import (
    DeleteRequest,
    GetRequest,
    KeysRequest,
    Request,
    SetRequest,
    encode_request,
)
from keyvalue.responses import (
    ErrorResponse,
    GetSuccessResponse,
    KeysSuccessResponse,
    MutationSuccessResponse,
    Response,
    parse_response,
)


class KeyValueClientError(Exception):
    pass


class Transport:
    def request(self, _request: Request) -> Response:
        raise NotImplementedError


class StreamTransport(Transport):
    # Generically makes a request over the socket
    def request(self, request: Request) -> Response:
        with self._create_client() as client:
            client.sendall(encode_request(request))

            raw_response = client.recv(4096)
            response = parse_response(raw_response)

            if isinstance(response, ErrorResponse):
                raise KeyValueClientError(f"unexpected response: {response!r}")

            return response

    def _create_client(self) -> socket.socket:
        raise NotImplementedError


class UnixSocketTransport(StreamTransport):
    def __init__(self, socket_path: Path):
        self.socket_path = socket_path

    def _create_client(self) -> socket.socket:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(self.socket_path))

        return client


class TcpSocketTransport(StreamTransport):
    def __init__(self, *, host: str, port: int):
        self.host = host
        self.port = port

    def _create_client(self) -> socket.socket:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))

        return client


class FifoTransport(Transport):
    def __init__(self, base_fifo_path: Path):
        self.base_fifo_path = base_fifo_path

    def request(self, request: Request) -> Response:
        request_path, response_path = fifo_paths(self.base_fifo_path)

        for path in (request_path, response_path):
            if not path.exists():
                raise RuntimeError("Server isn't running yet.")

        with open(request_path, "wb") as request_fifo:
            request_fifo.write(encode_request(request))
            request_fifo.flush()

        with open(response_path, "rb") as response_fifo:
            raw_response = response_fifo.readline().strip()

        response = parse_response(raw_response)

        if isinstance(response, ErrorResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")

        return response


class Client:
    def __init__(self, transport: Transport):
        self.transport = transport

    def get(self, key: str) -> str | None:
        response = self.transport.request(GetRequest(command="get", key=key))

        if not isinstance(response, GetSuccessResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")

        return response.value

    def set(self, key: str, value: str) -> None:
        response = self.transport.request(
            SetRequest(command="set", key=key, value=value)
        )

        if not isinstance(response, MutationSuccessResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")

    def keys(self) -> list[str]:
        response = self.transport.request(KeysRequest(command="keys"))

        if not isinstance(response, KeysSuccessResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")

        return response.keys

    def delete(self, key: str) -> None:
        response = self.transport.request(DeleteRequest(command="delete", key=key))

        if not isinstance(response, MutationSuccessResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")
