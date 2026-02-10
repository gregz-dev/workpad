class WorkpadError(Exception):
    """Base exception for Workpad."""
    pass

class NotFoundError(WorkpadError):
    """Raised when an entity is not found."""
    pass

class ValidationError(WorkpadError):
    """Raised when data validation fails."""
    pass

class StorageError(WorkpadError):
    """Raised when a storage operation fails."""
    pass

class LimitExceededError(WorkpadError):
    """Raised when a limit (e.g. content length) is exceeded."""
    pass
