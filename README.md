# Minisculedb

Minisculedb is a minimal, lightweight, in-memory key-value database server implemented in Python using raw sockets.

## Features

- **Socket-based server:** Clients can connect via TCP sockets to interact with the database.
- **Multithreaded:** Handles multiple concurrent client connections.
- **Commands:** Supports basic key-value operations:
  - `SET <key> <value> [type]`: Stores a value in the database. Supports parsing types like `int`, `float`, `str`, `bool`, `list`, and `dict`.
  - `GET <key>`: Retrieves a value from the database.
  - `DEL <key>`: Deletes a key-value pair from the database.
- **Verbose Mode**: Clients can toggle verbose/debug responses by sending `VERBOSE`.

## Quickstart

Start the server:
```bash
python main.py
```

Connect via `telnet` or `netcat` and send commands!
