class DomainError(Exception):
    """Base class for all domain errors."""

    def __init__(self, message: str):
        super().__init__(message)
        class_name = self.__class__.__name__
        # Convert from CamelCase to snake_case and remove 'Error' suffix
        self._code = (
            "".join(["_" + c.lower() if c.isupper() else c for c in class_name])
            .lstrip("_")
            .replace("_error", "")
        )
