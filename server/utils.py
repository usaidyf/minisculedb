import shlex
from .errors import (
    EmptyCommandError,
    InvalidCommandError,
    InvalidTypeError,
    InvalidValueError,
    TooFewArgumentsError,
    TooManyArgumentsError,
    ValueParsingError,
)


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
            raise ValueParsingError(f"Value parsing error for type {expected_type}")
    except ValueError:
        raise InvalidValueError(f"Invalid value for type {expected_type}")


def handle_command(command, db, verbose=False):
    """
    Handles the logic for processing commands sent by clients, including parsing, validation, and execution of GET, SET, and DEL operations on the in-memory data store.
    It also supports an optional verbose mode for more detailed responses.
    """
    parts = split_with_preserving_quotes(command.strip())
    cmd = parts[0]

    if cmd == "HELP":
        key = parts[1]
        if key.upper() == "GET":
            return (
                "<HELP:GET>",
                "GET command retrieves the value of a specified key.\nUsage: GET key\nExample: GET foo",
            )
        elif key.upper() == "SET":
            return (
                "<HELP:SET>",
                'SET command assigns a value to a specified key with an optional type.\nUsage: SET key value [type]\nExample:\n- SET foo 123 int\n- SET bar "hello world" str',
            )
        elif key.upper() == "DEL":
            return (
                "<HELP:DEL>",
                "DEL command deletes a specified key.\nUsage: DEL key\nExample: DEL foo",
            )
        elif key.upper() == "VERBOSE":
            return (
                "<HELP:VERBOSE>",
                "VERBOSE command is a standalone command that toggles verbose mode for detailed responses from the server.",
            )
        elif key.upper() == "EXIT":
            return (
                "<HELP:EXIT>",
                "EXIT command is a standalone command that disconnects the client from the server.",
            )

    if cmd == "SET":
        key, value = parts[1], parts[2]
        exp_type = parts[3] if len(parts) == 4 else "str"
        parsed_value = parse_value(value, exp_type, verbose=verbose)

        db.set(key, parsed_value)
        return (
            (
                "<SUCCESS:SET_VALUE>",
                f"SET: {key} = {parsed_value} (type: {exp_type})",
            )
            if verbose
            else "<SUCCESS:SET_VALUE>"
        )

    elif cmd == "GET":
        key = parts[1]

        if not db.exists(key):
            return (
                ("<ERROR:INVALID_KEY>", f"GET: {key} does not exist")
                if verbose
                else "<ERROR:INVALID_KEY>"
            )
        val = db.get(key)
        val_type = type(val).__name__
        val = str(val)
        if not val:
            return (
                (
                    "<ERROR:INVALID_KEY>",
                    f"GET: {key} has no value",
                )
                if verbose
                else "<ERROR:INVALID_KEY>"
            )
        return (
            ("<SUCCESS:GET_VALUE>", f"GET: {key} = {val} (type: {val_type})")
            if verbose
            else ("<SUCCESS:GET_VALUE>", val)
        )

    elif cmd == "DEL":
        key = parts[1]

        if db.delete(key):
            return (
                ("<SUCCESS:DELETED>", f"DEL: {key} deleted successfully")
                if verbose
                else "<SUCCESS:DELETED>"
            )
        else:
            return (
                ("<ERROR:INVALID_KEY>", f"DEL: {key} does not exist")
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
        raise EmptyCommandError("Empty command string")

    cmd = parts[0].upper()

    if cmd == "HELP" and parts_length > 2:
        raise TooManyArgumentsError("Too many arguments for HELP command")
    if cmd == "HELP" and parts_length == 2:
        help_cmd = parts[1].upper()
        if help_cmd not in {"GET", "SET", "DEL", "VERBOSE", "EXIT"}:
            raise InvalidCommandError(
                "Invalid command for HELP. Supported commands: GET, SET, DEL, VERBOSE, EXIT"
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
    if cmd not in {"GET", "SET", "DEL", "VERBOSE", "EXIT", "HELP"}:
        raise InvalidCommandError("Invalid command")

    # Return original string but with capitalized command
    original_cmd = command.strip()[: len(parts[0])]
    return cmd + command.strip()[len(original_cmd) :]
