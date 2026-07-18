# keyvalue.py

A small Python key/value store.

## Usage

Run the CLI through the `just server` recipe and pass a database file with
`--data`.

```sh
just server --data /tmp/db.json set name Alice
just server --data /tmp/db.json get name
```

The `get` command prints the value if the key exists. Missing keys print
nothing.

## Development

```sh
just check
```
