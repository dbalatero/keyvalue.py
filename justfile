format:
    uv run ruff format .

lint:
    uv run ruff check .

test:
    uv run pytest

server:
    uv run python -m keyvalue

check:
    just lint
    just test
