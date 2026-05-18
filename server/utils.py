import shlex
from .errors import (
    EmptyCommandError,
    InvalidCommandError,
    InvalidTypeError,
    InvalidValueError,
    TooFewArgumentsError,
    TooManyArgumentsError,
    ValueParsingError,
    InvalidKeyError,
)
from .response import Response


def parse_value(value, expected_type):
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
            raise ValueParsingError(f"Value parsing error for type {expected_type}")
    except ValueError:
        raise InvalidValueError(f"Invalid value for type {expected_type}")


def handle_command(command, db):
    """
    Handles the logic for processing commands sent by clients, including parsing, validation, and execution of GET, SET, and DEL operations on the in-memory data store.
    """
    parts = split_with_preserving_quotes(command.strip())
    cmd = parts[0]

    if cmd == "HELP":
        key = parts[1]
        if key.upper() == "GET":
            return Response(
                {"status": "SUCCESS", "action": "HELP_GET"},
                message="GET command retrieves the value of a specified key.\nUsage: GET key\nExample: GET foo",
            )
        elif key.upper() == "SET":
            return Response(
                {"status": "SUCCESS", "action": "HELP_SET"},
                message='SET command assigns a value to a specified key with an optional type.\nUsage: SET key value [type]\nExample:\n- SET foo 123 int\n- SET bar "hello world" str',
            )
        elif key.upper() == "DEL":
            return Response(
                {"status": "SUCCESS", "action": "HELP_DEL"},
                message="DEL command deletes a specified key.\nUsage: DEL key\nExample: DEL foo",
            )
        elif key.upper() == "EXIT":
            return Response(
                {"status": "SUCCESS", "action": "HELP_EXIT"},
                message="EXIT command is a standalone command that disconnects the client from the server.",
            )

    if cmd == "SET":
        key, value = parts[1], parts[2]
        exp_type = parts[3] if len(parts) == 4 else "str"
        parsed_value = parse_value(value, exp_type)

        db.set(key, parsed_value)
        return Response(
            {"status": "SUCCESS", "action": "SET_VALUE"},
            message=f"SET command executed:\n{key}:\n{parsed_value}\ntype: {exp_type}",
        )

    elif cmd == "GET":
        key = parts[1]

        if not db.exists(key):
            raise InvalidKeyError(f"GET: {key} does not exist")
        val = db.get(key)
        val_type = type(val).__name__
        val = str(val)
        return Response(
            {"status": "SUCCESS", "action": "GET_VALUE"},
            value=val,
            message=f"GET: {key} = {val} (type: {val_type})",
        )

    elif cmd == "DEL":
        key = parts[1]

        if db.delete(key):
            return Response(
                {"status": "SUCCESS", "action": "DELETED"},
                message=f"DEL: {key} deleted successfully",
            )
        else:
            raise InvalidKeyError(f"DEL: {key} does not exist")


def split_with_preserving_quotes(s):
    """
    Splits a string while preserving quoted substrings.
    Example: 'SET key "value with spaces"' -> ['SET', 'key', 'value with spaces']
    """
    return shlex.split(s)


def validate_command(command):
    """
    Validates the syntax and structure of incoming commands from clients, ensuring they conform to expected formats for GET, SET, DEL, and EXIT operations. It raises specific errors for various validation failures, such as incorrect argument counts or invalid command types.
    It also returns the original command string with the command part capitalized for consistent processing later on.
    """
    parts = split_with_preserving_quotes(command.strip())
    parts_length = len(parts)

    if parts_length == 0:
        raise EmptyCommandError("Empty command string")

    cmd = parts[0].upper()

    if cmd == "HELP" and parts_length > 2:
        raise TooManyArgumentsError("Too many arguments for HELP command")
    if cmd == "HELP" and parts_length == 2:
        help_cmd = parts[1].upper()
        if help_cmd not in {"GET", "SET", "DEL", "EXIT"}:
            raise InvalidCommandError(
                "Invalid command for HELP. Supported commands: GET, SET, DEL, EXIT"
            )

    if cmd == "SET" and parts_length > 4:
        raise TooManyArgumentsError("Too many arguments for SET command")
    if cmd == "SET" and parts_length < 3:
        raise TooFewArgumentsError("Too few arguments for SET command")
    if cmd == "SET" and parts_length == 4:
        exp_type = parts[3]
        if exp_type not in {"int", "float", "str", "bool", "list", "dict"}:
            raise InvalidTypeError("Invalid type for SET command")

    if (cmd == "GET" or cmd == "DEL") and parts_length > 2:
        raise TooManyArgumentsError("Too many arguments")
    if (cmd == "GET" or cmd == "DEL") and parts_length < 2:
        raise TooFewArgumentsError(f"Too few arguments for {cmd} command")
    if cmd not in {"GET", "SET", "DEL", "EXIT", "HELP"}:
        raise InvalidCommandError("Invalid command")

    # Return original string but with capitalized command
    original_cmd = command.strip()[: len(parts[0])]
    return cmd + command.strip()[len(original_cmd) :]
