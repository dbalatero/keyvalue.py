import pytest

from keyvalue.__main__ import main

# Using capsys to capture stdout/stderr in tests for inspection.


def test_cli_set_then_get_prints_value(tmp_path, capsys) -> None:
    data_path = tmp_path / "db.json"

    main(["--data", str(data_path), "set", "name", "Alice"])
    main(["--data", str(data_path), "get", "name"])

    captured = capsys.readouterr()

    assert captured.out == "Alice\n"
    assert captured.err == ""


def test_cli_get_missing_key_prints_nothing(tmp_path, capsys) -> None:
    data_path = tmp_path / "db.json"

    main(["--data", str(data_path), "get", "missing"])

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""


def test_cli_requires_data_flag(capsys) -> None:
    with pytest.raises(SystemExit) as error:
        main(["get", "name"])

    assert error.value.code == 2
    assert "--data" in capsys.readouterr().err


def test_cli_rejects_invalid_key(tmp_path) -> None:
    data_path = tmp_path / "db.json"

    with pytest.raises(ValueError, match="invalid key"):
        main(["--data", str(data_path), "get", "Invalid"])
