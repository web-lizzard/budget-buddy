from domain.exceptions.domain_exception import DomainError


class BudgetNameTooShortError(DomainError):
    """Exception raised when a budget name is too short."""

    def __init__(self, min_length: int):
        """Initialize with min length."""
        super().__init__(f"Budget name must be at least {min_length} characters long.")
