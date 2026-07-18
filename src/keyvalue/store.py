import json
from pathlib import Path

from keyvalue.keys import validate_key


class Store:
    def __init__(self, path: Path) -> None:
        self.path = path

    def get(self, key: str) -> str | None:
        validate_key(key)

        data = self._load()
        return data.get(key)

    def set(self, key: str, value: str) -> None:
        validate_key(key)

        data = self._load()
        data[key] = value
        self._save(data)

    def _load(self) -> dict[str, str]:
        if not self.path.exists():
            return {}

        with self.path.open() as file:
            return json.load(file)

    def _save(self, data: dict[str, str]) -> None:
        # Ensure parent dir exists
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # If we have a path of "/tmp/data.json", we want to make a temporary
        # "/tmp/data.json.tmp" file when writing, so if we crash mid-write we
        # don't corrupt the actual data.json file.
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")

        with tmp_path.open("w") as file:
            json.dump(data, file)

        # Once we write the entire dump to json, we can move it to the main
        # data file location.
        tmp_path.replace(self.path)
