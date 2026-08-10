# Overview

Throughout the course, you will work on a capstone project, a key-value server – a program that stores and retrieves data organized by key, like an on-disk hash map. By the end of the course, we'll have a multithreaded program with an IPC interface that can set, retrieve, and delete keys concurrently without data races. Each week has a core milestone, but there will also be ample opportunities for you to customize your project.

# Week 1

Let's use filesystem APIs to implement the core operations of the key-value server. Your program should have two commands: `get` and `set`. The `set` command takes a key and a value and writes it to disk, and the `get` command takes a key and prints the value, if it exists. Store all data in a single file (hard-coded path is fine). Use whatever data format you want – this is not a class on data structures or algorithms, so we won't focus on making the key-value server efficient.

- [x] Set up CI
- [x] Add key validator
- [x] Add basic store
- [x] Wire up store to the server program

# Week 2

Modify your program to create the database file with permissions locked down to the file's owner. Change your on-disk format to use multiple files: you can have one file per key, or do something fancier like allowing keys to have multiple parts such as `a.b.c` and store all `a.*` keys in the same file. Add commands to list all keys and to delete a key from the database.

- [x] Refactor file storage to use a file per key
- [x] Ensure chmod 700 on directory
- [x] Ensure chmod 600 on key files
- [x] Implement `keys` (list all keys)
- [x] Implement `delete (key)` (delete a key)

# Week 3

No milestone this week!

# Week 4

Turn your key-value store into a Unix domain socket server. Write a client subcommand that connects to the server and allows you to read and write keys. Add a mode that uses a FIFO instead of sockets for client–server communication.

- [x] Make a `server` command that listens for commands
  - [x] Define the wire format: one JSON request per line, one JSON response per line
  - [x] Add typed request models for `get`, `set`, `keys`, and `delete`
    - [x] Use a Python validation library like Pydantic for a Zod-like parser
    - [x] Validate keys at the protocol boundary using the existing key validator
    - [x] Reject unknown commands, missing fields, wrong field types, and invalid keys
  - [x] Add typed response models
    - [x] Successful `get`: `{ "ok": true, "value": "..." }`
    - [x] Missing `get`: `{ "ok": true, "value": null }`
    - [x] Successful `keys`: `{ "ok": true, "keys": [...] }`
    - [x] Successful mutation: `{ "ok": true }`
    - [x] Failed request: `{ "ok": false, "error": "..." }`
  - [x] Write unit tests for request parsing before adding socket code
  - [x] Write unit tests for response encoding before adding socket code
  - [x] Add a command handler function that takes a parsed request and a `Store`
    - [x] Test `get`, `set`, `keys`, and `delete` without sockets
    - [x] Test validation errors become error responses in an outer loop `process_request()` function
  - [x] Add a connection handler that reads one request from a connection and writes one response
    - [x] Test it with `socket.socketpair()` so the test does not need a real socket path
  - [x] Add the UNIX domain socket server loop
    - [x] Create the socket with `socket.AF_UNIX`
    - [x] Bind it to a socket path
    - [x] Listen for connections
    - [x] Accept connections in a loop
    - [x] Pass each accepted connection to the connection handler
    - [x] Clean up a stale socket file before binding
    - [x] Remove the socket file when the server exits
- [x] Make a `client` command that communicates over the domain socket
  - [x] Build request objects from CLI arguments
  - [x] Encode requests as newline-delimited JSON
  - [x] Connect to the UNIX socket path
  - [x] Send one request and read one response
  - [x] Print `get` values and `keys` results like the current CLI does
  - [x] Print or raise useful errors when the server returns `{ "ok": false }`
  - [x] Add integration tests with a server running in a background thread
- [x] Abstract out the client and server interfaces to allow for FIFO mode instead
  - [x] Do this after the UNIX socket path works
  - [x] Extract only the parts shared by UNIX sockets and FIFO mode
  - [x] Keep request parsing, response encoding, and store dispatch independent from the transport

# Week 6

Extend the client–server interface you added last week to support real networking. Add an `--ipc` flag to your server that can be `unix`, `fifo` (if you implemented it last week), `udp`, or `tcp`.

For UDP: implement your own reliable-message semantics, i.e., the client should detect if a message was received, and retry if not.

For TCP: make sure there is some way to detect message boundaries in the bytestream, so that a client can send multiple messages on the same connection.

Listen on port `uid + 1000` for UDP and port `uid + 2000` for TCP, where uid is your user ID as printed by id -u in the shell. For example, if id -u prints 1008, then use ports 2008 and 3008. This ensures that you don't interfere with your classmates.

- [x] Refactor transport and server to be classes with shared socket logic
- [x] Add `--mode` flags
- [x] Add `--host` and `--port` flags
- [x] Add `--mode tcp`
- [ ] Add `--mode udp`
