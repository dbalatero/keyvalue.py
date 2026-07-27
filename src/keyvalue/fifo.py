import os
from pathlib import Path

from keyvalue.commands import process_request
from keyvalue.store import Store


def fifo_paths(base_fifo_path: Path) -> tuple[Path, Path]:
    return (
        base_fifo_path.with_name(f"{base_fifo_path.name}.request"),
        base_fifo_path.with_name(f"{base_fifo_path.name}.response"),
    )


def _ensure_fifo_paths(base_fifo_path: Path) -> tuple[Path, Path]:
    paths = fifo_paths(base_fifo_path)

    for path in paths:
        if not os.path.exists(path):
            os.mkfifo(path, 0o644)

    return paths


def serve_fifo(base_fifo_path: Path, store: Store) -> None:
    paths = _ensure_fifo_paths(base_fifo_path)

    try:
        print("Server: waiting for a client...")

        while True:
            with open(paths[0], "rb") as request_fifo:
                print("Server: client connected")

                line = request_fifo.readline()
                if not line:
                    print("Server: client disconnected")
                    continue

            response = process_request(store, line)

            with open(paths[1], "wb") as response_fifo:
                response_fifo.write(response)
                response_fifo.flush()

    finally:
        for path in paths:
            # cleanup
            path.unlink(missing_ok=True)
