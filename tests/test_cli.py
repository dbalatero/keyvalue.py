import pytest

from keyvalue.__main__ import main

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


def test_cli_requires_data_flag(capsys) -> None:
    with pytest.raises(SystemExit) as error:
        main(["get", "name"])

    assert error.value.code == 2
    assert "--data" in capsys.readouterr().err


def test_cli_rejects_invalid_key(tmp_path) -> None:
    data_dir = tmp_path / "data"

    with pytest.raises(ValueError, match="invalid key"):
        main(["--data", str(data_dir), "get", "Invalid"])
