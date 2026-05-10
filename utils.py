import shlex


def parse_value(value, expected_type, verbose=False):
    """
    Parses and validates values based on their expected types.
    """
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
        raise MinisculeError(
            f"Invalid value for type {expected_type}", "<ERROR:INVALID_VALUE>"
        )


def handle_command(command, lock, data_store, verbose=False):
    """
    Handles the logic for processing commands sent by clients, including parsing, validation, and execution of GET, SET, and DEL operations on the in-memory data store.
    It also supports an optional verbose mode for more detailed responses.
    """
    parts = split_with_preserving_quotes(command.strip())
    cmd = parts[0]

    if cmd == "SET":
        key, value = parts[1], parts[2]
        exp_type = parts[3] if len(parts) == 4 else "str"
        parsed_value = parse_value(value, exp_type, verbose=verbose)

        with lock:
            data_store[key] = parsed_value
        return (
            (
                "<SUCCESS:SET_VALUE>",
                f"SET command executed: {key} = {parsed_value} (type: {exp_type})",
            )
            if verbose
            else "<SUCCESS:SET_VALUE>"
        )

    elif cmd == "GET":
        key = parts[1]

        if not key in data_store:
            return (
                ("<ERROR:INVALID_KEY>", f"key '{key}' does not exist")
                if verbose
                else "<ERROR:INVALID_KEY>"
            )
        with lock:
            val = data_store.get(key)
            val_type = type(val)
            val = str(val)
            if not val:
                return (
                    (
                        "<ERROR:INVALID_KEY>",
                        f"key '{key}' has no value",
                    )
                    if verbose
                    else "<ERROR:INVALID_KEY>"
                )
        return (
            ("<SUCCESS:GET_VALUE>", f"key: {key} | value: {val} | type: {val_type}")
            if verbose
            else ("SUCCESS:GET_VALUE", val)
        )

    elif cmd == "DEL":
        key = parts[1]

        with lock:
            if key in data_store:
                del data_store[key]
                return (
                    ("<SUCCESS:DELETED>", f"key '{key}' deleted successfully")
                    if verbose
                    else "<SUCCESS:DELETED>"
                )
            else:
                return (
                    ("<ERROR:INVALID_KEY>", f"key '{key}' does not exist")
                    if verbose
                    else "<ERROR:INVALID_KEY>"
                )


def split_with_preserving_quotes(s):
    """
    Splits a string while preserving quoted substrings.
    Example: 'SET key "value with spaces"' -> ['SET', 'key', 'value with spaces']
    """
    return shlex.split(s)


def validate_command(command, verbose=False):
    """
    Validates the syntax and structure of incoming commands from clients, ensuring they conform to expected formats for GET, SET, DEL, VERBOSE, and EXIT operations. It raises specific errors for various validation failures, such as incorrect argument counts or invalid command types.
    It also returns the original command string with the command part capitalized for consistent processing later on.
    """
    parts = split_with_preserving_quotes(command.strip())
    parts_length = len(parts)

    if parts_length == 0:
        raise MinisculeError("Empty command", "<ERROR:EMPTY_COMMAND_STRING>")

    cmd = parts[0].upper()

    if cmd == "SET" and parts_length > 4:
        raise MinisculeError("Too many arguments", "<ERROR:TOO_MANY_ARGS>")
    if cmd == "SET" and parts_length < 3:
        raise MinisculeError("Too few arguments", "<ERROR:TOO_FEW_ARGS>")
    if cmd == "SET" and parts_length == 4:
        exp_type = parts[3]
        if exp_type not in {"int", "float", "str", "bool", "list", "dict"}:
            raise MinisculeError("Invalid type for SET command", "<ERROR:INVALID_TYPE>")
    if (cmd == "GET" or cmd == "DEL") and parts_length > 2:
        raise MinisculeError("Too many arguments", "<ERROR:TOO_MANY_ARGS>")
    if cmd not in {"GET", "SET", "DEL", "VERBOSE", "EXIT"}:
        raise MinisculeError("Invalid command", "<ERROR:INVALID_COMMAND>")

    # Return original string but with capitalized command
    original_cmd = command.strip()[: len(parts[0])]
    return cmd + command.strip()[len(original_cmd) :]


class MinisculeError(Exception):
    """
    Custom exception class for handling specific errors in the Minisculedb application, allowing for more descriptive error messages and error codes that can be sent back to clients for better debugging and user experience.
    """
    def __init__(self, message, error_code="<ERROR:GENERIC>"):
        super().__init__(message)
        self.error_code = error_code
