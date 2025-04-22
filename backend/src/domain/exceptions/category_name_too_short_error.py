from .domain_exception import DomainError


class CategoryNameTooShortError(DomainError):
    """Exception raised when category name is too short."""

    def __init__(self, min_length: int):
        super().__init__(
            f"Category name cannot be shorter than {min_length} characters"
        )
