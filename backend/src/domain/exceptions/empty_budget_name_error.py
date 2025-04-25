from domain.exceptions.domain_exception import DomainError


class EmptyBudgetNameError(DomainError):
    """Exception raised when a budget name is empty."""

    def __init__(self):
        """Initialize the exception."""
        super().__init__("Budget name cannot be empty.")
