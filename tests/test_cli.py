from pathlib import Path

import pytest

from keyvalue.__main__ import build_parser, main
from server_helpers import RunningServer, start_socket_server, stop_server

# Using capsys to capture stdout/stderr in tests for inspection.


@pytest.fixture
def socket_server(tmp_path) -> RunningServer:
    server = start_socket_server(tmp_path)
    try:
        yield server
    finally:
        stop_server(server.process)


def run_client_command(server: RunningServer, args: list[str]) -> None:
    main(["--data", str(server.data_dir), "--socket", str(server.path), *args])


def test_cli_set_then_get_prints_value(socket_server, capsys) -> None:
    run_client_command(socket_server, ["set", "name", "Alice"])
    run_client_command(socket_server, ["get", "name"])

    captured = capsys.readouterr()

    assert captured.out == "OK\nAlice\n"
    assert captured.err == ""


def test_cli_get_missing_key_prints_nothing(socket_server, capsys) -> None:
    run_client_command(socket_server, ["get", "missing"])

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""


def test_cli_keys_prints_sorted_keys(socket_server, capsys) -> None:
    run_client_command(socket_server, ["set", "last_name", "Lovelace"])
    run_client_command(socket_server, ["set", "first_name", "Ada"])
    run_client_command(socket_server, ["set", "user.email", "ada@example.com"])
    run_client_command(socket_server, ["keys"])

    captured = capsys.readouterr()

    assert captured.out == "OK\nOK\nOK\nfirst_name\nlast_name\nuser.email\n"
    assert captured.err == ""


def test_cli_keys_prints_nothing_when_store_is_empty(socket_server, capsys) -> None:
    run_client_command(socket_server, ["keys"])

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""


def test_cli_delete_removes_existing_key(socket_server, capsys) -> None:
    run_client_command(socket_server, ["set", "name", "Alice"])
    run_client_command(socket_server, ["delete", "name"])
    run_client_command(socket_server, ["get", "name"])

    captured = capsys.readouterr()

    assert captured.out == "OK\nOK\n"
    assert captured.err == ""


def test_cli_delete_missing_key_prints_nothing(socket_server, capsys) -> None:
    run_client_command(socket_server, ["delete", "missing"])

    captured = capsys.readouterr()

    assert captured.out == "OK\n"
    assert captured.err == ""


def test_cli_delete_rejects_invalid_key(tmp_path) -> None:
    data_dir = tmp_path / "data"

    with pytest.raises(ValueError, match="invalid key"):
        main(["--data", str(data_dir), "delete", "Invalid"])


def test_cli_defaults_data_path() -> None:
    args = build_parser().parse_args(["get", "name"])

    assert args.data == Path("/tmp/keyvalue-data")


def test_cli_rejects_invalid_key(tmp_path) -> None:
    data_dir = tmp_path / "data"

    with pytest.raises(ValueError, match="invalid key"):
        main(["--data", str(data_dir), "get", "Invalid"])


def test_cli_defaults_socket_path() -> None:
    args = build_parser().parse_args(["--data", "/tmp/kvdata", "server"])

    assert args.socket == Path("/tmp/keyvalue.sock")


def test_cli_accepts_top_level_socket_path(tmp_path) -> None:
    socket_path = tmp_path / "keyvalue.sock"

    args = build_parser().parse_args(
        ["--data", "/tmp/kvdata", "--socket", str(socket_path), "server"]
    )

    assert args.socket == socket_path


def test_cli_allows_missing_subcommand_for_server_mode() -> None:
    args = build_parser().parse_args(["--data", "/tmp/kvdata"])

    assert args.command is None
