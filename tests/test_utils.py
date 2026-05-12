from server.utils import validate_command, handle_command, parse_value, MinisculeError
import pytest
import threading


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

    # Invalid commands
    with pytest.raises(MinisculeError) as excinfo:
        assert validate_command("SET key1 value2 but with spaces and longer str")
    assert excinfo.value.error_code == "<ERROR:TOO_MANY_ARGS>"

    with pytest.raises(MinisculeError) as excinfo:
        validate_command("")
    assert excinfo.value.error_code == "<ERROR:EMPTY_COMMAND_STRING>"

    with pytest.raises(MinisculeError) as excinfo:
        validate_command("SET key1 value1 str extra_arg")
    assert excinfo.value.error_code == "<ERROR:TOO_MANY_ARGS>"

    with pytest.raises(MinisculeError) as excinfo:
        validate_command("GET key1 extra_arg")
    assert excinfo.value.error_code == "<ERROR:TOO_MANY_ARGS>"

    with pytest.raises(MinisculeError) as excinfo:
        validate_command("UNKNOWN_CMD key1")
    assert excinfo.value.error_code == "<ERROR:INVALID_COMMAND>"


def test_handle_command():
    # Mocking a simple data store and lock
    DATA_STORE = {}
    LOCK = threading.Lock()

    # Test SET command
    assert handle_command("SET key1 value1", LOCK, DATA_STORE) == "<SUCCESS:SET_VALUE>"
    assert DATA_STORE["key1"] == "value1"

    assert (
        handle_command('SET key1 "value2 with spaces"', LOCK, DATA_STORE)
        == "<SUCCESS:SET_VALUE>"
    )
    assert DATA_STORE["key1"] == "value2 with spaces"

    assert handle_command("SET key2 123 int", LOCK, DATA_STORE) == "<SUCCESS:SET_VALUE>"
    assert DATA_STORE["key2"] == 123

    assert (
        handle_command("SET key3 45.67 float", LOCK, DATA_STORE)
        == "<SUCCESS:SET_VALUE>"
    )
    assert DATA_STORE["key3"] == 45.67

    assert (
        handle_command("SET key4 true bool", LOCK, DATA_STORE) == "<SUCCESS:SET_VALUE>"
    )
    assert DATA_STORE["key4"] is True

    assert (
        handle_command("SET key5 1,2,3 list", LOCK, DATA_STORE) == "<SUCCESS:SET_VALUE>"
    )
    assert DATA_STORE["key5"] == ["1", "2", "3"]

    assert (
        handle_command("SET key6 key:value dict", LOCK, DATA_STORE)
        == "<SUCCESS:SET_VALUE>"
    )
    assert DATA_STORE["key6"] == {"key": "value"}

    # Test GET command
    result = handle_command("GET key1", LOCK, DATA_STORE)
    assert result == ("<SUCCESS:GET_VALUE>", "value2 with spaces")
    assert (
        handle_command("GET non_existent_key", LOCK, DATA_STORE)
        == "<ERROR:INVALID_KEY>"
    )

    # Test DEL command
    assert handle_command("DEL key1", LOCK, DATA_STORE) == "<SUCCESS:DELETED>"
    assert "key1" not in DATA_STORE
    assert (
        handle_command("DEL non_existent_key", LOCK, DATA_STORE)
        == "<ERROR:INVALID_KEY>"
    )


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
    assert excinfo.value.error_code == "<ERROR:INVALID_VALUE>"

    with pytest.raises(MinisculeError) as excinfo:
        parse_value("not_a_dict", "dict")
    assert excinfo.value.error_code == "<ERROR:INVALID_VALUE>"

    with pytest.raises(MinisculeError) as excinfo:
        parse_value("123", "unsupported_type")
    assert excinfo.value.error_code == "<ERROR:VALUE_PARSING_ERROR>"
