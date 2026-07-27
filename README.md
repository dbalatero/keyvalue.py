# keyvalue.py

[![CI](https://github.com/dbalatero/keyvalue.py/actions/workflows/ci.yml/badge.svg)](https://github.com/dbalatero/keyvalue.py/actions/workflows/ci.yml)

A small Python key/value store for [CS644](https://iafisher.com/cs644/summer2026).

## Usage

Run the server:

```sh
just server
just server --help
```

Once the server is running, you can point the client at it:

```sh
# set value
just client set name Alice

# get value
just client get name

# list keys
just client keys

# delete key
just client delete name
```

### Modes

By default, the KV store runs on UNIX domain sockets (`--socket /path/to/some.socket`).

If you want to communicate over bi-directional FIFO pipes, you can pass in `--fifo /tmp/fifo` to use `/tmp/fifo.request` and `/tmp/fifo.response` for communication.

## Development

```sh
# Runs tests, linters, formatters
just check

# Runs tests
just test

# Run a specific test
just test tests/test_some_test.py
```
