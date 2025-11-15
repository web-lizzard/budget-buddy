from pydantic.utils import to_snake_lower


class CoreError(Exception):
    """Base class for all core errors."""

    def __init__(self, message: str | None = None) -> None:
        self.message = message or "An unknown error occurred"
        self.type = to_snake_lower(self.__class__.__name__.replace("Error", ""))
        super().__init__(self.message)
