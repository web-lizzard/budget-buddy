from domain.exceptions.domain_exception import DomainError


class TransactionNotFoundError(DomainError):
    """Exception raised when a transaction is not found."""

    def __init__(self, transaction_id: str):
        super().__init__(f"Transaction with ID {transaction_id} not found.")
