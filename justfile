format:
    uv run ruff format .

format-check:
    uv run ruff format --check .

lint:
    uv run ruff check .

test *args:
    uv run pytest {{args}}

server *args:
    uv run python -m keyvalue {{args}}

check:
    just format-check
    just lint
    just test
