from .domain_exception import DomainError


class InvalidTransferPolicyError(DomainError):
    """Exception raised when transaction transfer policy is invalid."""

    def __init__(self, message: str):
        super().__init__(message)
