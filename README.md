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

By default, the KV store runs in UNIX domain socket mode.

If you want to communicate over bi-directional FIFO pipes, pass `--mode fifo`.

## Development

```sh
# Runs tests, linters, formatters
just check

# Runs tests
just test

# Run a specific test
just test tests/test_some_test.py
```
