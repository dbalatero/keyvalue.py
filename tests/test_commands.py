from keyvalue.commands import handle_command
from keyvalue.requests import DeleteRequest, GetRequest, KeysRequest, SetRequest
from keyvalue.responses import (
    GetSuccessResponse,
    KeysSuccessResponse,
    MutationSuccessResponse,
)
from keyvalue.store import Store


def test_handle_get_command_returns_existing_value(tmp_path) -> None:
    store = Store(tmp_path / "data")
    store.set("name", "Alice")

    response = handle_command(store, GetRequest(command="get", key="name"))

    assert response == GetSuccessResponse(ok=True, value="Alice")


def test_handle_get_command_returns_none_for_missing_key(tmp_path) -> None:
    store = Store(tmp_path / "data")

    response = handle_command(store, GetRequest(command="get", key="missing"))

    assert response == GetSuccessResponse(ok=True, value=None)


def test_handle_set_command_stores_value(tmp_path) -> None:
    store = Store(tmp_path / "data")

    response = handle_command(
        store,
        SetRequest(command="set", key="name", value="Alice"),
    )

    assert response == MutationSuccessResponse(ok=True)
    assert store.get("name") == "Alice"


def test_handle_set_command_overwrites_existing_value(tmp_path) -> None:
    store = Store(tmp_path / "data")
    store.set("name", "Alice")

    response = handle_command(
        store,
        SetRequest(command="set", key="name", value="Bob"),
    )

    assert response == MutationSuccessResponse(ok=True)
    assert store.get("name") == "Bob"


def test_handle_delete_command_removes_existing_key(tmp_path) -> None:
    store = Store(tmp_path / "data")
    store.set("name", "Alice")

    response = handle_command(store, DeleteRequest(command="delete", key="name"))

    assert response == MutationSuccessResponse(ok=True)
    assert store.get("name") is None


def test_handle_delete_command_succeeds_for_missing_key(tmp_path) -> None:
    store = Store(tmp_path / "data")

    response = handle_command(store, DeleteRequest(command="delete", key="missing"))

    assert response == MutationSuccessResponse(ok=True)


def test_handle_keys_command_returns_sorted_keys(tmp_path) -> None:
    store = Store(tmp_path / "data")
    store.set("last_name", "Lovelace")
    store.set("first_name", "Ada")

    response = handle_command(store, KeysRequest(command="keys"))

    assert response == KeysSuccessResponse(ok=True, keys=["first_name", "last_name"])


def test_handle_keys_command_returns_empty_list_when_store_is_empty(tmp_path) -> None:
    store = Store(tmp_path / "data")

    response = handle_command(store, KeysRequest(command="keys"))

    assert response == KeysSuccessResponse(ok=True, keys=[])
