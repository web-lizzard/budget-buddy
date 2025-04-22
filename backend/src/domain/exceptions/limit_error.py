from .domain_exception import DomainError


class InvalidLimitValueError(DomainError):
    """Exception raised when limit value is invalid."""

    def __init__(self, value):
        super().__init__(f"Invalid limit value: {value}")
