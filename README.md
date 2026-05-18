# MinisculeDB

MinisculeDB is a minimal, lightweight, in-memory key-value database server implemented in Python using raw sockets.

## Features

- **Socket-based server:** Clients can connect via TCP sockets to interact with the database.
- **Multithreaded:** Handles multiple concurrent client connections with thread-safe data access.
- **Structured Responses:** Uses a formalized response format containing status codes, return values, and explanatory messages.
- **Commands:** Supports basic key-value operations:
  - `SET <key> <value> [type]`: Stores a value in the database. Supports parsing types like `int`, `float`, `str`, `bool`, `list`, and `dict`.
  - `GET <key>`: Retrieves a value from the database.
  - `DEL <key>`: Deletes a key-value pair from the database.
  - `HELP [command]`: Shows help messages or details about a specific command.

## Quickstart

It is recommended to use a virtual environment for running and testing the project.

1. **Create and activate a virtual environment using <a href="https://docs.astral.sh/uv/getting-started/installation/" target="_blank">uv</a>:**
   ```bash
   uv venv
   ```
   ```bash
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows:
   .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set environment variables: (using .env file)**
   ```bash
   cp .env.example .env
   ```
   This will create a new .env file, you can update it to your preferences.

4. **Start the server:**
   ```bash
   uv run minisculedb-server
   ```

5. **Connect:**
   Connect via `telnet` or `netcat` and send commands!

## Testing

The project uses `pytest` for testing. After setting up the virtual environment and installing dependencies you can optionally run the tests using:

```bash
uv run pytest
```
