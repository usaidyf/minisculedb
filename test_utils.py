from utils import validate_command, handle_command, parse_value, MinisculeError
import pytest
import threading


def test_validate_command():
    # Valid commands
    assert validate_command("SET key1 value1") == "SET key1 value1"
    assert validate_command("GET key1") == "GET key1"
    assert validate_command("DEL key1") == "DEL key1"

    # Invalid commands
    with pytest.raises(MinisculeError) as excinfo:
        validate_command("")
    assert excinfo.value.error_code == "<EMPTY_COMMAND_STRING>"

    with pytest.raises(MinisculeError) as excinfo:
        validate_command("SET key1 value1 str extra_arg")
    assert excinfo.value.error_code == "<TOO_MANY_ARGS>"

    with pytest.raises(MinisculeError) as excinfo:
        validate_command("GET key1 extra_arg")
    assert excinfo.value.error_code == "<TOO_MANY_ARGS>"

    with pytest.raises(MinisculeError) as excinfo:
        validate_command("UNKNOWN_CMD key1")
    assert excinfo.value.error_code == "<INVALID_COMMAND>"


def test_handle_command():
    # Mocking a simple data store and lock
    DATA_STORE = {}
    LOCK = threading.Lock()

    # Test SET command
    assert handle_command("SET key1 value1", LOCK, DATA_STORE) == "<OK>"
    assert DATA_STORE["key1"] == "value1"

    # Test GET command
    assert handle_command("GET key1", LOCK, DATA_STORE) == "value1"
    assert handle_command("GET non_existent_key", LOCK, DATA_STORE) == "<INVALID_KEY>"

    # Test DEL command
    assert handle_command("DEL key1", LOCK, DATA_STORE) == "<DELETED>"
    assert "key1" not in DATA_STORE
    assert handle_command("DEL non_existent_key", LOCK, DATA_STORE) == "<INVALID_KEY>"


def test_parse_value():
    assert parse_value("123", "int") == 123
    assert parse_value("45.67", "float") == 45.67
    assert parse_value("true", "bool") is True
    assert parse_value("false", "bool") is False
    assert parse_value("1,2,3", "list") == ["1", "2", "3"]
    assert parse_value("key:value", "dict") == {"key": "value"}
    assert parse_value("some string", "str") == "some string"

    with pytest.raises(MinisculeError) as excinfo:
        parse_value("not_an_int", "int")
    assert excinfo.value.error_code == "<INVALID_VALUE>"

    with pytest.raises(MinisculeError) as excinfo:
        parse_value("not_a_dict", "dict")
    assert excinfo.value.error_code == "<INVALID_VALUE>"

    with pytest.raises(MinisculeError) as excinfo:
        parse_value("123", "unsupported_type")
    assert excinfo.value.error_code == "<VALUE_PARSING_ERROR>"
