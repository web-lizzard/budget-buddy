from domain.exceptions.domain_exception import DomainError


class StatisticsRecordNotFoundError(DomainError):
    """Exception raised when a statistics record is not found."""

    def __init__(self, message: str):
        super().__init__(message)
