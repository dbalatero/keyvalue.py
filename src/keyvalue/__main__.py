import argparse
import os
from pathlib import Path

from keyvalue.client import (
    Client,
    FifoTransport,
    TcpSocketTransport,
    UnixSocketTransport,
)
from keyvalue.fifo import serve_fifo
from keyvalue.sockets import TcpSocketServer, UnixSocketServer
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
        "--mode",
        choices=("socket", "fifo", "tcp"),
        default="socket",
        help="transport mode",
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
        default=Path("/tmp/keyvalue"),
        help="path prefix for the FIFO communication pipes",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="hostname to run the tcp server on",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=os.getuid() + 2000,
        help="port to run the tcp server on",
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

    transport = None
    match args.mode:
        case "socket":
            transport = UnixSocketTransport(args.socket)
        case "fifo":
            transport = FifoTransport(args.fifo)
        case "tcp":
            transport = TcpSocketTransport(host=args.host, port=args.port)
        case _:
            raise ValueError("did not handle mode")

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
            print(f"Running in {args.mode} mode")

            if args.mode == "socket":
                print(f"Listening at {args.socket}")

                server = UnixSocketServer(store=store, socket_path=args.socket)
                server.serve()
            elif args.mode == "tcp":
                print(f"Listening on TCP at {args.host}:{args.port}")
                server = TcpSocketServer(store=store, host=args.host, port=args.port)
                server.serve()
            else:
                serve_fifo(args.fifo, store)

        case _:
            raise ValueError(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
