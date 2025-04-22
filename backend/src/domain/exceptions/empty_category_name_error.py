from .domain_exception import DomainError


class EmptyCategoryNameError(DomainError):
    """Exception raised when category name is empty or None."""

    def __init__(self):
        super().__init__("Category name cannot be empty")
