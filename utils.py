def parse_value(value, expected_type):
    try:
        if expected_type == "int":
            return int(value)
        elif expected_type == "float":
            return float(value)
        elif expected_type == "str":
            return str(value)
        elif expected_type == "bool":
            if value.lower() in {"true", "1"}:
                return True
            elif value.lower() in {"false", "0"}:
                return False
            else:
                raise ValueError("Invalid boolean string")
        elif expected_type == "list":
            return value.split(",")
        elif expected_type == "dict":
            items = value.split(",")
            result = {}
            for item in items:
                key, val = item.split(":")
                result[key.strip()] = val.strip()
            return result
        else:
            raise MinisculeError(f"Value parsing error", "<ERROR:VALUE_PARSING_ERROR>")
    except ValueError:
        raise MinisculeError(f"Invalid value for type {expected_type}", "<ERROR:INVALID_VALUE>")


def handle_command(command, LOCK, DATA_STORE):
    parts = command.split()
    cmd = parts[0]

    if cmd == "SET":
        key, value = parts[1], parts[2]
        exp_type = parts[3] if len(parts) == 4 else "str"
        parsed_value = parse_value(value, exp_type)

        with LOCK:
            DATA_STORE[key] = parsed_value
        return "<SUCCESS:OK>"

    elif cmd == "GET":
        key = parts[1]

        if not key in DATA_STORE:
            return "<ERROR:INVALID_KEY>"
        with LOCK:
            val = str(DATA_STORE.get(key))
        return val if val else "<ERROR:INVALID_KEY>"

    elif cmd == "DEL":
        key = parts[1]

        with LOCK:
            if key in DATA_STORE:
                del DATA_STORE[key]
                return "<SUCCESS:DELETED>"
            else:
                return "<ERROR:INVALID_KEY>"


def validate_command(command):
    parts = command.split()
    parts_length = len(parts)

    if parts_length == 0:
        raise MinisculeError("Empty command", "<ERROR:EMPTY_COMMAND_STRING>")

    cmd = parts[0].upper()

    if cmd == "SET" and parts_length > 4:
        raise MinisculeError("Too many arguments", "<ERROR:TOO_MANY_ARGS>")
    if cmd == "SET" and parts_length < 2:
        raise MinisculeError("Too few arguments", "<ERROR:TOO_FEW_ARGS>")
    if cmd == "SET" and parts_length == 4:
        exp_type = parts[3]
        if exp_type not in {"int", "float", "str", "bool", "list", "dict"}:
            raise MinisculeError("Invalid type for SET command", "<ERROR:INVALID_TYPE>")
    if (cmd == "GET" or cmd == "DEL") and parts_length > 2:
        raise MinisculeError("Too many arguments", "<ERROR:TOO_MANY_ARGS>")
    if cmd not in {"GET", "SET", "DEL"}:
        raise MinisculeError("Invalid command", "<ERROR:INVALID_COMMAND>")

    return f"{cmd} " + " ".join(parts[1:])


class MinisculeError(Exception):
    def __init__(self, message, error_code="<ERROR:GENERIC>"):
        super().__init__(message)
        self.error_code = error_code
