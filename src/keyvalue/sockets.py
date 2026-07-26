import socket

from keyvalue.commands import process_request
from keyvalue.store import Store


def handle_connection(conn: socket.socket, store: Store) -> None:
    raw_request = conn.recv(4096).decode("utf-8")
    response = process_request(store, raw_request)

    conn.sendall(response)
