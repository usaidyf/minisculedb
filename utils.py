def handle_command(command, LOCK, DATA_STORE):
    parts = command.split()
    cmd = parts[0]

    if cmd == "SET":
        key, value = parts[1], parts[2]

        with LOCK:
            DATA_STORE[key] = value
        return "<OK>"

    elif cmd == "GET":
        key = parts[1]

        with LOCK:
            val = DATA_STORE.get(key)
        return val if val else "<INVALID_KEY>"

    elif cmd == "DEL":
        key = parts[1]

        with LOCK:
            if key in DATA_STORE:
                del DATA_STORE[key]
                return "<DELETED>"
            else:
                return "<INVALID_KEY>"


def validate_command(command):
    parts = command.split()
    parts_length = len(parts)

    if parts_length == 0:
        raise MinisculeError("Empty command", "<EMPTY_COMMAND_STRING>")

    cmd = parts[0].upper()

    if cmd == "SET" and parts_length > 3:
        raise MinisculeError("Too many arguments", "<TOO_MANY_ARGS>")
    if (cmd == "GET" or cmd == "DEL") and parts_length > 2:
        raise MinisculeError("Too many arguments", "<TOO_MANY_ARGS>")
    if cmd not in {"GET", "SET", "DEL"}:
        raise MinisculeError("Invalid command", "<INVALID_COMMAND>")

    return f"{cmd} " + " ".join(parts[1:])


class MinisculeError(Exception):
    def __init__(self, message, error_code="<GENERIC>"):
        super().__init__(message)
        self.error_code = error_code
