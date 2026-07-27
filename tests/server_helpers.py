import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from keyvalue.client import Client, FifoTransport, KeyValueClientError, SocketTransport


@dataclass(frozen=True)
class RunningServer:
    process: subprocess.Popen[bytes]
    data_dir: Path
    mode: Literal["socket", "fifo"]
    path: Path


def wait_until_server_ready(
    process: subprocess.Popen[bytes],
    client: Client,
) -> None:
    deadline = time.monotonic() + 2
    last_error = None

    while time.monotonic() < deadline:
        try:
            client.keys()
            return
        except (KeyValueClientError, OSError, RuntimeError) as error:
            last_error = error
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=1)
                raise AssertionError(
                    "server exited before accepting requests\n"
                    f"stdout:\n{stdout.decode()}\n"
                    f"stderr:\n{stderr.decode()}"
                ) from error

            time.sleep(0.01)

    raise AssertionError(f"server did not become ready: {last_error}")


def start_server(tmp_path: Path, mode: Literal["socket", "fifo"]) -> RunningServer:
    repo_root = Path(__file__).parents[1]
    data_dir = tmp_path / "data"
    path = tmp_path / ("keyvalue.sock" if mode == "socket" else "keyvalue")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    mode_args = ["--socket", str(path)] if mode == "socket" else ["--fifo", str(path)]

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "keyvalue",
            "--data",
            str(data_dir),
            *mode_args,
            "server",
        ],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    transport = SocketTransport(path) if mode == "socket" else FifoTransport(path)
    wait_until_server_ready(process, Client(transport))

    return RunningServer(
        process=process,
        data_dir=data_dir,
        mode=mode,
        path=path,
    )


def start_socket_server(tmp_path: Path) -> RunningServer:
    return start_server(tmp_path, "socket")


def start_fifo_server(tmp_path: Path) -> RunningServer:
    return start_server(tmp_path, "fifo")


def stop_server(process: subprocess.Popen[bytes]) -> None:
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2)
