

class ApplicationException(Exception):
    """Base exception class for all application-specific exceptions."""
    DEFAULT_MESSAGE = "An unexpected error occurred"
    ERROR_CODE = 5000

    def __init__(self, message: str = None, error_code: int = None):
        self.message = message or self.DEFAULT_MESSAGE
        self.error_code = error_code or self.ERROR_CODE
        super().__init__(self.message)

class ThreadException(ApplicationException):
    """Base exception class for all thread-related exceptions."""
    ERROR_CODE = 1250

class ThreadUpdateError(ThreadException):
    DEFAULT_MESSAGE = "Thread update failed: Thread not found"
    ERROR_CODE = 1251


class ThreadDeleteError(ThreadException):
    DEFAULT_MESSAGE = "Thread deletion failed: Thread not found"
    ERROR_CODE = 1252
