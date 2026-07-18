format:
    uv run ruff format .

lint:
    uv run ruff check .

test:
    uv run pytest

check:
    just lint
    just test
