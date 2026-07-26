import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from keyvalue.store import Store


# TODO: swap in the real client once we write it
def send_request(
    socket_path: Path,
    request: bytes,
    process: subprocess.Popen[bytes],
) -> bytes:
    deadline = time.monotonic() + 2
    last_error = None

    while time.monotonic() < deadline:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(str(socket_path))
                client.sendall(request)
                return client.recv(4096)
        except OSError as error:
            last_error = error
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=1)
                raise AssertionError(
                    "server exited before accepting requests\n"
                    f"stdout:\n{stdout.decode()}\n"
                    f"stderr:\n{stderr.decode()}"
                ) from error

            time.sleep(0.01)

    raise AssertionError(f"could not connect to server: {last_error}")


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
        set_response = send_request(
            socket_path,
            b'{"command":"set","key":"name","value":"Alice"}\n',
            process,
        )
        get_response = send_request(
            socket_path,
            b'{"command":"get","key":"name"}\n',
            process,
        )
        error_response = send_request(
            socket_path,
            b'{"command":"get","key":"Invalid"}\n',
            process,
        )

        assert set_response == b'{"ok":true}\n'
        assert get_response == b'{"ok":true,"value":"Alice"}\n'
        assert b'"ok":false' in error_response
        assert b"invalid key" in error_response
        assert Store(data_dir).get("name") == "Alice"
    finally:
        stop_server(process)
