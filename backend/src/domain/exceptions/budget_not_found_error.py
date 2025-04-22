from .domain_exception import DomainError


class BudgetNotFoundError(DomainError):
    """Raised when budget is not found."""

    def __init__(self, budget_id: str):
        super().__init__(f"Budget with id {budget_id} not found")
