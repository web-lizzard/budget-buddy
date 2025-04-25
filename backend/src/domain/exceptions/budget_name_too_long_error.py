from domain.exceptions.domain_exception import DomainError


class BudgetNameTooLongError(DomainError):
    """Exception raised when a budget name is too long."""

    def __init__(self, max_length: int):
        """Initialize with max length."""
        super().__init__(f"Budget name cannot be longer than {max_length} characters.")
