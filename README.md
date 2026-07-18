# keyvalue.py

[![CI](https://github.com/dbalatero/keyvalue.py/actions/workflows/ci.yml/badge.svg)](https://github.com/dbalatero/keyvalue.py/actions/workflows/ci.yml)

A small Python key/value store for [CS644](https://iafisher.com/cs644/summer2026).

## Usage

Run the CLI through the `just server` recipe and pass a database file with
`--data`.

```sh
# set value
just server --data /tmp/kvdata set name Alice

# get value
just server --data /tmp/kvdata get name

# list keys
just server --data /tmp/kvdata keys

# delete key
just server --data /tmp/kvdata delete name
```

## Development

```sh
just check
```
