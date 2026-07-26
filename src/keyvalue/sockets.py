import socket
from pathlib import Path

from keyvalue.commands import process_request
from keyvalue.store import Store


def create_server_socket(socket_path: Path) -> socket.socket:
    # Get a fresh socket each time
    socket_path.unlink(missing_ok=True)

    sock = socket.socket(
        socket.AF_UNIX,  # unix domain socket
        socket.SOCK_STREAM,  # create with stream interface
    )

    try:
        sock.bind(str(socket_path))
        sock.listen()
    except Exception:
        # Let's cleanup here, in case we hit an exception
        sock.close()
        raise

    return sock


def accept_one(sock: socket.socket, store: Store) -> None:
    conn, _ = sock.accept()
    with conn:
        handle_connection(conn, store)


def handle_connection(conn: socket.socket, store: Store) -> None:
    raw_request = conn.recv(4096).decode("utf-8")
    response = process_request(store, raw_request)

    conn.sendall(response)


def serve(socket_path: Path, store: Store) -> None:
    with create_server_socket(socket_path) as sock:
        while True:
            accept_one(sock, store)
