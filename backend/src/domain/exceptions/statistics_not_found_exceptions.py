from domain.exceptions.domain_exception import DomainError


class StatisticsNotFoundError(DomainError):
    """Exception raised when statistics are not found."""

    def __init__(self, message: str):
        super().__init__(message)
