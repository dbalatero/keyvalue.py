from pathlib import Path

import pytest

from keyvalue.__main__ import build_parser, main

# Using capsys to capture stdout/stderr in tests for inspection.


def test_cli_set_then_get_prints_value(tmp_path, capsys) -> None:
    data_dir = tmp_path / "data"

    main(["--data", str(data_dir), "set", "name", "Alice"])
    main(["--data", str(data_dir), "get", "name"])

    captured = capsys.readouterr()

    assert captured.out == "Alice\n"
    assert captured.err == ""


def test_cli_get_missing_key_prints_nothing(tmp_path, capsys) -> None:
    data_dir = tmp_path / "data"

    main(["--data", str(data_dir), "get", "missing"])

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""


def test_cli_keys_prints_sorted_keys(tmp_path, capsys) -> None:
    data_dir = tmp_path / "data"

    main(["--data", str(data_dir), "set", "last_name", "Lovelace"])
    main(["--data", str(data_dir), "set", "first_name", "Ada"])
    main(["--data", str(data_dir), "set", "user.email", "ada@example.com"])
    main(["--data", str(data_dir), "keys"])

    captured = capsys.readouterr()

    assert captured.out == "first_name\nlast_name\nuser.email\n"
    assert captured.err == ""


def test_cli_keys_prints_nothing_when_store_is_empty(tmp_path, capsys) -> None:
    data_dir = tmp_path / "data"

    main(["--data", str(data_dir), "keys"])

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""


def test_cli_delete_removes_existing_key(tmp_path, capsys) -> None:
    data_dir = tmp_path / "data"

    main(["--data", str(data_dir), "set", "name", "Alice"])
    main(["--data", str(data_dir), "delete", "name"])
    main(["--data", str(data_dir), "get", "name"])

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""


def test_cli_delete_missing_key_prints_nothing(tmp_path, capsys) -> None:
    data_dir = tmp_path / "data"

    main(["--data", str(data_dir), "delete", "missing"])

    captured = capsys.readouterr()

    assert captured.out == ""
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
