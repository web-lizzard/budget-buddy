from domain.exceptions.domain_exception import DomainError


class DuplicateCategoryNameError(DomainError):
    """Raised when trying to add a category with a name that already exists."""

    def __init__(self, category_name: str):
        message = f"Category with name '{category_name}' already exists in this budget"
        super().__init__(message)
