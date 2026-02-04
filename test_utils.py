from utils import validate_command, handle_command, MinisculeError
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
        validate_command("SET key1 value1 extra_arg")
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
