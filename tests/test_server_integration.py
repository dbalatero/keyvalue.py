import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from keyvalue.client import Client, KeyValueClientError
from keyvalue.store import Store


def wait_until_server_ready(
    process: subprocess.Popen[bytes],
    socket_path: Path,
) -> None:
    client = Client(socket_path)
    deadline = time.monotonic() + 2
    last_error = None

    while time.monotonic() < deadline:
        try:
            client.keys()
            return
        except (KeyValueClientError, OSError) as error:
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


def send_request(
    socket_path: Path,
    request: bytes,
) -> bytes:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(str(socket_path))
        client.sendall(request)
        return client.recv(4096)


def stop_server(process: subprocess.Popen[bytes]) -> None:
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2)


def test_server_process_handles_client_requests(tmp_path) -> None:
    repo_root = Path(__file__).parents[1]
    data_dir = tmp_path / "data"
    socket_path = tmp_path / "keyvalue.sock"
    client = Client(socket_path)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "keyvalue",
            "--data",
            str(data_dir),
            "--socket",
            str(socket_path),
            "server",
        ],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        wait_until_server_ready(process, socket_path)

        client.set("name", "Alice")
        assert client.get("name") == "Alice"
        assert client.keys() == ["name"]

        client.set("foo", "bar")
        assert client.keys() == ["foo", "name"]

        client.delete("foo")
        assert client.keys() == ["name"]
        assert client.get("foo") is None

        client.set("name", "Jeff")
        assert client.get("name") == "Jeff"
    finally:
        stop_server(process)
