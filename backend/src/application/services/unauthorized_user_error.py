from domain.exceptions import DomainError


class UnauthorizedUserError(DomainError):
    """Exception raised when a user is not authorized to perform an action."""

    pass
