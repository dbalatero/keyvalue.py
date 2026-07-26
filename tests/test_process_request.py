import json

from keyvalue.commands import process_request
from keyvalue.store import Store


def test_process_request_handles_get_command(tmp_path) -> None:
    store = Store(tmp_path / "data")
    store.set("name", "Alice")

    response = process_request(store, '{"command": "get", "key": "name"}')

    assert response == b'{"ok":true,"value":"Alice"}\n'


def test_process_request_handles_set_command(tmp_path) -> None:
    store = Store(tmp_path / "data")

    response = process_request(
        store,
        '{"command": "set", "key": "name", "value": "Alice"}',
    )

    assert response == b'{"ok":true}\n'
    assert store.get("name") == "Alice"


def test_process_request_turns_parse_error_into_error_response(tmp_path) -> None:
    store = Store(tmp_path / "data")

    response = process_request(store, '{"command": "get", "key": "Invalid"}')

    response_body = json.loads(response)
    assert response_body["ok"] is False
    assert "invalid key" in response_body["message"]


def test_process_request_turns_handler_error_into_error_response(
    tmp_path,
    monkeypatch,
) -> None:
    store = Store(tmp_path / "data")

    def fail_get(key: str) -> str | None:
        raise OSError("disk is unavailable")

    monkeypatch.setattr(store, "get", fail_get)

    response = process_request(store, '{"command": "get", "key": "name"}')

    assert response == b'{"ok":false,"message":"disk is unavailable"}\n'
