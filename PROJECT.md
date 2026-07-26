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

- [ ] Make a `server` command that listens for commands
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
  - [ ] Add a command handler function that takes a parsed request and a `Store`
    - [ ] Test `get`, `set`, `keys`, and `delete` without sockets
    - [ ] Test validation errors become error responses
  - [ ] Add a connection handler that reads one request from a connection and writes one response
    - [ ] Test it with `socket.socketpair()` so the test does not need a real socket path
  - [ ] Add the UNIX domain socket server loop
    - [ ] Create the socket with `socket.AF_UNIX`
    - [ ] Bind it to a socket path
    - [ ] Listen for connections
    - [ ] Accept connections in a loop
    - [ ] Pass each accepted connection to the connection handler
    - [ ] Clean up a stale socket file before binding
    - [ ] Remove the socket file when the server exits
- [ ] Make a `client` command that communicates over the domain socket
  - [ ] Build request objects from CLI arguments
  - [ ] Encode requests as newline-delimited JSON
  - [ ] Connect to the UNIX socket path
  - [ ] Send one request and read one response
  - [ ] Print `get` values and `keys` results like the current CLI does
  - [ ] Print or raise useful errors when the server returns `{ "ok": false }`
  - [ ] Add integration tests with a server running in a background thread
- [ ] Abstract out the client and server interfaces to allow for FIFO mode instead
  - [ ] Do this after the UNIX socket path works
  - [ ] Extract only the parts shared by UNIX sockets and FIFO mode
  - [ ] Keep request parsing, response encoding, and store dispatch independent from the transport
