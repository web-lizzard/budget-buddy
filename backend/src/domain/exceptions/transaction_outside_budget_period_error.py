from domain.exceptions.domain_exception import DomainError


class TransactionOutsideBudgetPeriodError(DomainError):
    """Raised when a transaction date is outside the budget period."""

    def __init__(self):
        message = "Transaction date is outside the budget period"
        super().__init__(message)
