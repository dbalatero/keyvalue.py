import socket
from pathlib import Path

from keyvalue.commands import process_request
from keyvalue.responses import ErrorResponse, encode_response
from keyvalue.store import Store

MAX_REQUEST_BYTES = 1024 * 1024


class RequestTooLargeError(Exception):
    pass


class SocketServer:
    def __init__(self, *, store: Store):
        self.store = store

    def serve(self) -> None:
        with self._create_socket() as sock:
            while True:
                self._accept_one(sock)

    def _create_socket(self) -> socket.socket:
        raise NotImplementedError

    def _accept_one(self, sock: socket.socket) -> None:
        conn, _ = sock.accept()
        with conn:
            self._handle_connection(conn)

    def _handle_connection(self, conn: socket.socket) -> None:
        try:
            raw_request = self._read_request(conn).decode("utf-8")
            response = process_request(self.store, raw_request)

            conn.sendall(response)
        except RequestTooLargeError:
            response = encode_response(
                ErrorResponse(ok=False, message="request is too large")
            )
            conn.sendall(response)

    def _read_request(self, conn: socket.socket) -> bytes:
        chunks = []
        bytes_read = 0

        while True:
            chunk = conn.recv(4096)
            if chunk == b"":
                break

            bytes_read += len(chunk)
            if bytes_read > MAX_REQUEST_BYTES:
                raise RequestTooLargeError("request is too large")

            chunks.append(chunk)

            if b"\n" in chunk:
                break

        return b"".join(chunks)


class UnixSocketServer(SocketServer):
    def __init__(self, *, store: Store, socket_path: Path):
        super().__init__(store=store)
        self.socket_path = socket_path

    def _create_socket(self) -> socket.socket:
        # Get a fresh socket each time
        self.socket_path.unlink(missing_ok=True)

        sock = socket.socket(
            socket.AF_UNIX,  # unix domain socket
            socket.SOCK_STREAM,  # create with stream interface
        )

        try:
            sock.bind(str(self.socket_path))
            sock.listen()
        except Exception:
            # Let's cleanup here, in case we hit an exception
            sock.close()
            raise

        return sock


class TcpSocketServer(SocketServer):
    def __init__(self, *, store: Store, host: str, port: int):
        super().__init__(store=store)
        self.host = host
        self.port = port

    def _create_socket(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # The OS might keep around recently closed TCP connections, so this
            # will ensure we can do address reuse if we run the server again
            # quickly.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen()
        except Exception:
            sock.close()
            raise

        return sock
