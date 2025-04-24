from domain.exceptions.domain_exception import DomainError


class CannotRenewDeactivatedBudgetError(DomainError):
    """Raised when trying to renew a deactivated budget."""

    def __init__(self, budget_id: str):
        message = f"Cannot renew deactivated budget: {budget_id}"
        super().__init__(message)
