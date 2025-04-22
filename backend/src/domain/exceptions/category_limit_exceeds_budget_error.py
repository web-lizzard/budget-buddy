from domain.exceptions.domain_exception import DomainError


class CategoryLimitExceedsBudgetError(DomainError):
    """Raised when category limit would exceed budget total limit."""

    def __init__(self, category_name: str, category_limit: str, available_limit: str):
        message = f"Category '{category_name}' with limit {category_limit} exceeds available budget limit of {available_limit}"
        super().__init__(message)
