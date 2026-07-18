import argparse
from pathlib import Path

from keyvalue.store import Store


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="keyvalue")
    parser.add_argument(
        "--data",
        required=True,
        type=Path,
        help="path to the database file",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("key")

    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("key")
    set_parser.add_argument("value")

    subparsers.add_parser("keys")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    store = Store(args.data)

    match args.command:
        case "get":
            value = store.get(args.key)
            if value is not None:
                print(value)
            return

        case "set":
            store.set(args.key, args.value)
            return

        case "keys":
            for key in store.keys():
                print(key)
            return

        case _:
            raise ValueError(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
