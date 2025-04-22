from dataclasses import dataclass

from domain.exceptions import CurrencyMismatchError, InvalidLimitValueError

from .money import Money


@dataclass(frozen=True)
class Limit:
    """
    Value object representing a spending limit.
    """

    value: Money

    def __post_init__(self):
        """
        Validate the limit value after initialization.

        Raises:
            InvalidLimitValueError: If the limit value is negative
        """
        if self.value.amount < 0:
            raise InvalidLimitValueError("Limit cannot be negative")

    def is_exceeded(self, current_spending: "Limit") -> bool:
        """
        Check if the limit is exceeded.

        Args:
            current_spending: Current spending as Money object

        Returns:
            True if limit is exceeded, False otherwise

        Raises:
            CurrencyMismatchError: If currencies don't match
        """
        value = current_spending.value
        if value.currency != self.value.currency:
            raise InvalidLimitValueError(
                f"Currency mismatch: limit is in {self.value.currency}, spending is in {value.currency}"
            )

        return value.amount > self.value.amount

    def add(self, other: "Limit") -> "Limit":
        """
        Add two limits together.
        """
        return Limit(value=self.value.add(other.value))

    def remaining_amount(self, current_spending: Money) -> Money:
        """
        Calculate the remaining amount.

        Args:
            current_spending: Current spending as Money object

        Returns:
            Remaining amount as Money object

        Raises:
            CurrencyMismatchError: If currencies don't match
        """

        if current_spending.currency != self.value.currency:
            raise CurrencyMismatchError(
                currency1=current_spending.currency, currency2=self.value.currency
            )

        if current_spending.amount >= self.value.amount:
            return Money(0, self.value.currency)

        return Money(self.value.amount - current_spending.amount, self.value.currency)

    def __str__(self) -> str:
        return f"Limit: {self.value}"
