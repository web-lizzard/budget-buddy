from domain.exceptions.domain_exception import DomainError


class MaxCategoriesReachedError(DomainError):
    """Raised when trying to add more categories than allowed."""

    def __init__(self, max_categories: int):
        message = f"Cannot add more categories. Maximum of {max_categories} categories allowed"
        super().__init__(message)
