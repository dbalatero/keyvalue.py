import os
from pathlib import Path

from keyvalue.keys import validate_key


class Store:
    def __init__(self, data_directory: Path) -> None:
        self.data_directory = data_directory
        self._ensure_data_directory()

    def get(self, key: str) -> str | None:
        validate_key(key)

        path = self._key_path(key)
        if not path.exists():
            return None

        return path.read_text()

    def set(self, key: str, value: str) -> None:
        validate_key(key)

        # Target path
        path = self._key_path(key)

        # Temp path so we avoid issues if we crash during writes
        tmp_path = path.with_name(f".{path.name}.tmp")
        fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(fd, "w") as file:
                file.write(value)

            tmp_path.replace(path)
            path.chmod(0o600)  # paranoia
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise

    def _ensure_data_directory(self) -> None:
        if not os.path.isdir(self.data_directory):
            os.makedirs(self.data_directory, mode=0o700, exist_ok=True)

        # Ensure the data directory is only readable by the user, even if it
        # exists already
        os.chmod(self.data_directory, 0o700)

    def _key_path(self, key: str) -> Path:
        return self.data_directory / key
