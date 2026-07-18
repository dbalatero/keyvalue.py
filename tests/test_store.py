import pytest

from keyvalue.store import Store


def mode(path) -> int:
    return path.stat().st_mode & 0o777


def test_get_missing_key_returns_none(tmp_path) -> None:
    store = Store(tmp_path / "data")

    assert store.get("missing") is None


def test_set_then_get_returns_value(tmp_path) -> None:
    store = Store(tmp_path / "data")

    store.set("name", "Alice")

    assert store.get("name") == "Alice"


def test_set_writes_value_to_file_named_after_key(tmp_path) -> None:
    data_dir = tmp_path / "data"
    store = Store(data_dir)

    store.set("name", "Alice")

    assert (data_dir / "name").read_text() == "Alice"


def test_set_writes_key_file_with_owner_only_permissions(tmp_path) -> None:
    data_dir = tmp_path / "data"
    store = Store(data_dir)

    store.set("name", "Alice")

    assert mode(data_dir / "name") == 0o600


def test_store_creates_data_directory_with_owner_only_permissions(tmp_path) -> None:
    data_dir = tmp_path / "data"

    Store(data_dir)

    assert mode(data_dir) == 0o700


def test_store_restricts_existing_data_directory_permissions(tmp_path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(mode=0o777)
    data_dir.chmod(0o777)

    Store(data_dir)

    assert mode(data_dir) == 0o700


def test_get_reads_value_from_file_named_after_key(tmp_path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "name").write_text("Alice")
    store = Store(data_dir)

    assert store.get("name") == "Alice"


def test_set_overwrites_existing_value(tmp_path) -> None:
    store = Store(tmp_path / "data")

    store.set("name", "Alice")
    store.set("name", "Bob")

    assert store.get("name") == "Bob"


def test_store_persists_values_across_instances(tmp_path) -> None:
    path = tmp_path / "data"

    Store(path).set("name", "Alice")

    assert Store(path).get("name") == "Alice"


def test_get_rejects_invalid_key(tmp_path) -> None:
    store = Store(tmp_path / "data")

    with pytest.raises(ValueError, match="invalid key"):
        store.get("Invalid")


def test_set_rejects_invalid_key(tmp_path) -> None:
    store = Store(tmp_path / "data")

    with pytest.raises(ValueError, match="invalid key"):
        store.set("Invalid", "value")
