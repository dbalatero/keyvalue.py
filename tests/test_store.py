import pytest

from keyvalue.store import Store


def test_get_missing_key_returns_none(tmp_path) -> None:
    store = Store(tmp_path / "db.json")

    assert store.get("missing") is None


def test_empty_database_file_is_treated_as_empty(tmp_path) -> None:
    path = tmp_path / "db.json"
    path.write_text("")
    store = Store(path)

    assert store.get("missing") is None


def test_set_then_get_returns_value(tmp_path) -> None:
    store = Store(tmp_path / "db.json")

    store.set("name", "Alice")

    assert store.get("name") == "Alice"


def test_set_overwrites_existing_value(tmp_path) -> None:
    store = Store(tmp_path / "db.json")

    store.set("name", "Alice")
    store.set("name", "Bob")

    assert store.get("name") == "Bob"


def test_store_persists_values_across_instances(tmp_path) -> None:
    path = tmp_path / "db.json"

    Store(path).set("name", "Alice")

    assert Store(path).get("name") == "Alice"


def test_get_rejects_invalid_key(tmp_path) -> None:
    store = Store(tmp_path / "db.json")

    with pytest.raises(ValueError, match="invalid key"):
        store.get("Invalid")


def test_set_rejects_invalid_key(tmp_path) -> None:
    store = Store(tmp_path / "db.json")

    with pytest.raises(ValueError, match="invalid key"):
        store.set("Invalid", "value")
