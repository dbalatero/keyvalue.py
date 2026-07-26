import pytest

from keyvalue.requests import RequestParseError, parse_request


def test_get_request_parses_correctly() -> None:
    json = '{"command": "get", "key": "foo"}'
    request = parse_request(json)

    assert request.command == "get"
    assert request.key == "foo"


def test_set_request_parses_correctly() -> None:
    json = '{"command": "set", "key": "foo", "value": "bar"}'
    request = parse_request(json)

    assert request.command == "set"
    assert request.key == "foo"
    assert request.value == "bar"


def test_delete_request_parses_correctly() -> None:
    json = '{"command": "delete", "key": "foo"}'
    request = parse_request(json)

    assert request.command == "delete"
    assert request.key == "foo"


def test_keys_request_parses_correctly() -> None:
    json = '{"command": "keys"}'
    request = parse_request(json)

    assert request.command == "keys"


def test_request_rejects_unknown_command() -> None:
    json = '{"command": "unknown", "key": "foo"}'

    with pytest.raises(RequestParseError):
        parse_request(json)


def test_get_request_rejects_missing_key() -> None:
    json = '{"command": "get"}'

    with pytest.raises(RequestParseError):
        parse_request(json)


def test_set_request_rejects_missing_value() -> None:
    json = '{"command": "set", "key": "foo"}'

    with pytest.raises(RequestParseError):
        parse_request(json)


def test_get_request_rejects_invalid_key() -> None:
    json = '{"command": "get", "key": "Invalid"}'

    with pytest.raises(RequestParseError):
        parse_request(json)
