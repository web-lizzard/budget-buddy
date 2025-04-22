from domain.exceptions.domain_exception import DomainError


class CategoryNotFoundError(DomainError):
    """Raised when a category is not found in the budget."""

    def __init__(self, category_id: str):
        message = f"Category with ID '{category_id}' not found in this budget"
        super().__init__(message)
