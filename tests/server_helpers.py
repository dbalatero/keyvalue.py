import os
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from keyvalue.client import (
    Client,
    FifoTransport,
    KeyValueClientError,
    TcpSocketTransport,
    UnixSocketTransport,
)


@dataclass(frozen=True)
class RunningServer:
    process: subprocess.Popen[bytes]
    data_dir: Path
    mode: Literal["socket", "fifo", "tcp"]
    path: Path | None = None
    host: str | None = None
    port: int | None = None


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


def reserve_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_server(
    tmp_path: Path,
    mode: Literal["socket", "fifo", "tcp"],
) -> RunningServer:
    repo_root = Path(__file__).parents[1]
    data_dir = tmp_path / "data"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    path = None
    host = None
    port = None

    if mode == "socket":
        path = tmp_path / "keyvalue.sock"
        mode_args = ["--mode", "socket", "--socket", str(path)]
        transport = UnixSocketTransport(path)
    elif mode == "fifo":
        path = tmp_path / "keyvalue"
        mode_args = ["--mode", "fifo", "--fifo", str(path)]
        transport = FifoTransport(path)
    else:
        host = "127.0.0.1"
        port = reserve_tcp_port()
        mode_args = ["--mode", "tcp", "--host", host, "--port", str(port)]
        transport = TcpSocketTransport(host=host, port=port)

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

    wait_until_server_ready(process, Client(transport))

    return RunningServer(
        process=process,
        data_dir=data_dir,
        mode=mode,
        path=path,
        host=host,
        port=port,
    )


def start_socket_server(tmp_path: Path) -> RunningServer:
    return start_server(tmp_path, "socket")


def start_fifo_server(tmp_path: Path) -> RunningServer:
    return start_server(tmp_path, "fifo")


def start_tcp_server(tmp_path: Path) -> RunningServer:
    return start_server(tmp_path, "tcp")


def stop_server(process: subprocess.Popen[bytes]) -> None:
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2)
