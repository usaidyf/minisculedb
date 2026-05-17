from server.database import MinisculeDatabase
from server.utils import validate_command, handle_command, parse_value
from server.errors import (
    EmptyCommandError,
    InvalidCommandError,
    TooFewArgumentsError,
    TooManyArgumentsError,
    InvalidValueError,
    ValueParsingError,
)
import pytest


def test_validate_command():
    # Valid commands
    assert validate_command("SET key1 value1") == "SET key1 value1"
    assert (
        validate_command('SET key1 "value2 but with spaces, quotes and longer" str')
        == 'SET key1 "value2 but with spaces, quotes and longer" str'
    )

    # With different types
    assert validate_command("SET key2 123 int") == "SET key2 123 int"
    assert validate_command("SET key3 45.67 float") == "SET key3 45.67 float"
    assert validate_command("SET key4 true bool") == "SET key4 true bool"
    assert validate_command("SET key5 1,2,3 list") == "SET key5 1,2,3 list"
    assert validate_command("SET key6 key:value dict") == "SET key6 key:value dict"

    assert validate_command("GET key1") == "GET key1"
    assert validate_command("DEL key1") == "DEL key1"

    # Help commands
    assert validate_command("HELP") == "HELP"
    assert validate_command("HELP GET") == "HELP GET"
    assert validate_command("HELP SET") == "HELP SET"
    assert validate_command("HELP DEL") == "HELP DEL"
    assert validate_command("HELP VERBOSE") == "HELP VERBOSE"
    assert validate_command("HELP EXIT") == "HELP EXIT"

    # Invalid commands
    with pytest.raises(TooManyArgumentsError) as excinfo:
        assert validate_command("SET key1 value2 but with spaces and longer str")
    assert excinfo.value.error_code == "<ERROR:TOO_MANY_ARGS>"

    with pytest.raises(InvalidCommandError) as excinfo:
        validate_command("HELP UNKNOWN")
    assert excinfo.value.error_code == "<ERROR:INVALID_COMMAND>"

    with pytest.raises(TooManyArgumentsError) as excinfo:
        validate_command("HELP GET EXTRA")
    assert excinfo.value.error_code == "<ERROR:TOO_MANY_ARGS>"

    with pytest.raises(EmptyCommandError) as excinfo:
        validate_command("")
    assert excinfo.value.error_code == "<ERROR:EMPTY_COMMAND_STRING>"

    with pytest.raises(TooManyArgumentsError) as excinfo:
        validate_command("SET key1 value1 str extra_arg")
    assert excinfo.value.error_code == "<ERROR:TOO_MANY_ARGS>"

    with pytest.raises(TooManyArgumentsError) as excinfo:
        validate_command("GET key1 extra_arg")
    assert excinfo.value.error_code == "<ERROR:TOO_MANY_ARGS>"

    with pytest.raises(TooFewArgumentsError) as excinfo:
        validate_command("GET")
    assert excinfo.value.error_code == "<ERROR:TOO_FEW_ARGS>"

    with pytest.raises(TooFewArgumentsError) as excinfo:
        validate_command("DEL")
    assert excinfo.value.error_code == "<ERROR:TOO_FEW_ARGS>"

    with pytest.raises(InvalidCommandError) as excinfo:
        validate_command("UNKNOWN_CMD key1")
    assert excinfo.value.error_code == "<ERROR:INVALID_COMMAND>"


def test_handle_command():
    # Mocking a simple data store and lock
    test_db = MinisculeDatabase()

    # Test SET command
    assert handle_command("SET key1 value1", test_db) == "<SUCCESS:SET_VALUE>"
    assert test_db.get("key1") == "value1"

    assert (
        handle_command('SET key1 "value2 with spaces"', test_db)
        == "<SUCCESS:SET_VALUE>"
    )
    assert test_db.get("key1") == "value2 with spaces"

    assert handle_command("SET key2 123 int", test_db) == "<SUCCESS:SET_VALUE>"
    assert test_db.get("key2") == 123

    assert handle_command("SET key3 45.67 float", test_db) == "<SUCCESS:SET_VALUE>"
    assert test_db.get("key3") == 45.67

    assert handle_command("SET key4 true bool", test_db) == "<SUCCESS:SET_VALUE>"
    assert test_db.get("key4") is True

    assert handle_command("SET key5 1,2,3 list", test_db) == "<SUCCESS:SET_VALUE>"
    assert test_db.get("key5") == ["1", "2", "3"]

    assert handle_command("SET key6 key:value dict", test_db) == "<SUCCESS:SET_VALUE>"
    assert test_db.get("key6") == {"key": "value"}

    assert handle_command('SET key7 ""', test_db) == "<SUCCESS:SET_VALUE>"
    assert test_db.get("key7") == ""

    # Test GET command
    result = handle_command("GET key1", test_db)
    assert result == ("<SUCCESS:GET_VALUE>", "value2 with spaces")
    assert handle_command("GET key7", test_db) == ("<SUCCESS:GET_VALUE>", "")

    assert handle_command("GET non_existent_key", test_db, verbose=True) == (
        "<ERROR:INVALID_KEY>",
        "GET: non_existent_key does not exist",
    )

    # Test DEL command
    assert handle_command("DEL key1", test_db) == "<SUCCESS:DELETED>"
    assert test_db.exists("key1") is False
    assert handle_command("DEL non_existent_key", test_db) == "<ERROR:INVALID_KEY>"

    # Test HELP command
    assert handle_command("HELP GET", test_db)[0] == "<HELP:GET>"
    assert handle_command("HELP SET", test_db)[0] == "<HELP:SET>"
    assert handle_command("HELP DEL", test_db)[0] == "<HELP:DEL>"
    assert handle_command("HELP VERBOSE", test_db)[0] == "<HELP:VERBOSE>"
    assert handle_command("HELP EXIT", test_db)[0] == "<HELP:EXIT>"


def test_parse_value():
    assert parse_value("123", "int") == 123
    assert parse_value("45.67", "float") == 45.67
    assert parse_value("true", "bool") is True
    assert parse_value("false", "bool") is False
    assert parse_value("1,2,3", "list") == ["1", "2", "3"]
    assert parse_value("key:value", "dict") == {"key": "value"}
    assert parse_value("some string", "str") == "some string"

    with pytest.raises(InvalidValueError) as excinfo:
        parse_value("not_an_int", "int")
    assert excinfo.value.error_code == "<ERROR:INVALID_VALUE>"

    with pytest.raises(InvalidValueError) as excinfo:
        parse_value("not_a_dict", "dict")
    assert excinfo.value.error_code == "<ERROR:INVALID_VALUE>"

    with pytest.raises(ValueParsingError) as excinfo:
        parse_value("123", "unsupported_type")
    assert excinfo.value.error_code == "<ERROR:VALUE_PARSING_ERROR>"
