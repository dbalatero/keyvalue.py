import pytest

from keyvalue.keys import validate_key


@pytest.mark.parametrize(
    "key",
    [
        "name",
        "_user",
        "123",
        "user_1",
        "user.name",
        "1.2.3",
    ],
)
def test_validate_key_accepts_valid_keys(key: str) -> None:
    validate_key(key)


@pytest.mark.parametrize(
    "key",
    [
        "",
        ".name",
        "name.",
        "user..name",
        "User",
        "user-name",
        "user name",
    ],
)
def test_validate_key_rejects_invalid_keys(key: str) -> None:
    with pytest.raises(ValueError):
        validate_key(key)
