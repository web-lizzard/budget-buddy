from domain.exceptions.domain_exception import DomainError


class CannotAddTransactionToDeactivatedBudgetError(DomainError):
    """Raised when trying to add a transaction to a deactivated budget with date after deactivation."""

    def __init__(self, transaction_date: str, deactivation_date: str):
        message = f"Cannot add transaction with date {transaction_date} to deactivated budget (deactivation date: {deactivation_date})"
        super().__init__(message)
