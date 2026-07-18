import re

_KEY_PATTERN = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")

_KEY_ERROR = (
  "invalid key: keys must contain lowercase letters, numbers, or underscores, "
  "with optional dot-separated segments"
)

def validate_key(key: str) -> None:
    if not _KEY_PATTERN.fullmatch(key):
        raise ValueError(f"{_KEY_ERROR}; got {key!r}")
