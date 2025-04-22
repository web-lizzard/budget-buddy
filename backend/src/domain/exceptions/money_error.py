from . import DomainError


class InvalidCurrencyError(DomainError):
    """Exception raised when currency is invalid."""

    def __init__(self, currency):
        super().__init__(f"Invalid currency: {currency}")


class CurrencyMismatchError(DomainError):
    """Exception raised when trying to perform operations between different currencies."""

    def __init__(self, currency1, currency2):
        super().__init__(
            f"Cannot perform operation between different currencies: {currency1} and {currency2}"
        )
