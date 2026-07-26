import socket
from pathlib import Path

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


class Client:
    def __init__(self, socket_path: Path):
        self.socket_path = socket_path

    def get(self, key: str) -> str | None:
        response = self._make_request(GetRequest(command="get", key=key))

        if not isinstance(response, GetSuccessResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")

        return response.value

    def set(self, key: str, value: str) -> None:
        response = self._make_request(SetRequest(command="set", key=key, value=value))

        if not isinstance(response, MutationSuccessResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")

    def keys(self) -> list[str]:
        response = self._make_request(KeysRequest(command="keys"))

        if not isinstance(response, KeysSuccessResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")

        return response.keys

    def delete(self, key: str) -> None:
        response = self._make_request(DeleteRequest(command="delete", key=key))

        if not isinstance(response, MutationSuccessResponse):
            raise KeyValueClientError(f"unexpected response: {response!r}")

    # Generically makes a request over the socket
    def _make_request(self, request: Request) -> Response:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(self.socket_path))
            client.sendall(encode_request(request))

            raw_response = client.recv(4096)
            response = parse_response(raw_response)

            if isinstance(response, ErrorResponse):
                raise KeyValueClientError(f"unexpected response: {response!r}")

            return response
