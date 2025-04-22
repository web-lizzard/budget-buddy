from .domain_exception import DomainError


class CategoryNameTooLongError(DomainError):
    """Exception raised when category name is too long."""

    def __init__(self, max_length: int):
        super().__init__(f"Category name cannot be longer than {max_length} characters")
