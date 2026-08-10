import socket
from pathlib import Path

from keyvalue.commands import process_request
from keyvalue.store import Store


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
        raw_request = conn.recv(4096).decode("utf-8")
        response = process_request(self.store, raw_request)

        conn.sendall(response)


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
