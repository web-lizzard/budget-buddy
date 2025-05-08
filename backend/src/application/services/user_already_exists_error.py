from domain.exceptions import DomainError


class UserAlreadyExistsError(DomainError):
    """Exception raised when a user already exists."""

    pass
