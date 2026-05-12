class MinisculeError(Exception):
    """
    Custom exception class for handling specific errors in the Minisculedb application, allowing for more descriptive error messages and error codes that can be sent back to clients for better debugging and user experience.
    """

    def __init__(self, message, error_code="<ERROR:GENERIC>"):
        super().__init__(message)
        self.error_code = error_code


class ValueParsingError(MinisculeError):
    def __init__(self, message="Value parsing error"):
        super().__init__(message, "<ERROR:VALUE_PARSING_ERROR>")


class InvalidCommandError(MinisculeError):
    def __init__(self, message="Invalid command"):
        super().__init__(message, "<ERROR:INVALID_COMMAND>")


class TooManyArgumentsError(MinisculeError):
    def __init__(self, message="Too many arguments"):
        super().__init__(message, "<ERROR:TOO_MANY_ARGS>")


class TooFewArgumentsError(MinisculeError):
    def __init__(self, message="Too few arguments"):
        super().__init__(message, "<ERROR:TOO_FEW_ARGS>")


class EmptyCommandError(MinisculeError):
    def __init__(self, message="Empty command string"):
        super().__init__(message, "<ERROR:EMPTY_COMMAND_STRING>")


class InvalidKeyError(MinisculeError):
    def __init__(self, message="Invalid key"):
        super().__init__(message, "<ERROR:INVALID_KEY>")

class InvalidTypeError(MinisculeError):
    def __init__(self, message="Invalid type specified"):
        super().__init__(message, "<ERROR:INVALID_TYPE>")

class InvalidValueError(MinisculeError):
    def __init__(self, message="Invalid value"):
        super().__init__(message, "<ERROR:INVALID_VALUE>")
