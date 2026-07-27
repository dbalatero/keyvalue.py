import argparse
from pathlib import Path

from keyvalue.client import Client, FifoTransport, SocketTransport
from keyvalue.fifo import serve_fifo
from keyvalue.sockets import serve_socket
from keyvalue.store import Store


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="keyvalue")
    parser.add_argument(
        "--data",
        default=Path("/tmp/keyvalue-data"),
        type=Path,
        help="path to the database file",
    )
    parser.add_argument(
        "--socket",
        type=Path,
        default=Path("/tmp/keyvalue.sock"),
        help="path to the UNIX domain socket",
    )
    parser.add_argument(
        "--fifo",
        type=Path,
        default=None,
        help="path prefix for the FIFO communication pipes",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("key")

    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("key")
    set_parser.add_argument("value")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("key")

    subparsers.add_parser("keys")
    subparsers.add_parser("server")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command is None:
        args.command = "server"

    mode = "fifo" if args.fifo else "socket"
    socket_path = args.socket

    transport = (
        SocketTransport(socket_path) if mode == "socket" else FifoTransport(args.fifo)
    )

    client = Client(transport)

    match args.command:
        case "get":
            value = client.get(args.key)
            if value is not None:
                print(value)
            return

        case "set":
            client.set(args.key, args.value)
            print("OK")
            return

        case "keys":
            for key in client.keys():
                print(key)
            return

        case "delete":
            client.delete(args.key)
            print("OK")
            return

        case "server":
            store = Store(args.data)
            print(f"Running in {mode} mode")

            if mode == "socket":
                print("Listening at", args.socket)

                serve_socket(socket_path, store)
            else:
                serve_fifo(args.fifo, store)

        case _:
            raise ValueError(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
