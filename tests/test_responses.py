from keyvalue.responses import (
    ErrorResponse,
    GetSuccessResponse,
    KeysSuccessResponse,
    MutationSuccessResponse,
    encode_response,
)


def test_mutation_success_response_encodes_correctly() -> None:
    response = MutationSuccessResponse(ok=True)

    assert encode_response(response) == b'{"ok":true}\n'


def test_get_success_response_with_value_encodes_correctly() -> None:
    response = GetSuccessResponse(ok=True, value="bar")

    assert encode_response(response) == b'{"ok":true,"value":"bar"}\n'


def test_get_success_response_with_missing_value_encodes_correctly() -> None:
    response = GetSuccessResponse(ok=True, value=None)

    assert encode_response(response) == b'{"ok":true,"value":null}\n'


def test_keys_success_response_encodes_correctly() -> None:
    response = KeysSuccessResponse(ok=True, keys=["first_name", "last_name"])

    assert (
        encode_response(response) == b'{"ok":true,"keys":["first_name","last_name"]}\n'
    )


def test_error_response_encodes_correctly() -> None:
    response = ErrorResponse(ok=False, message="invalid key")

    assert encode_response(response) == b'{"ok":false,"message":"invalid key"}\n'
