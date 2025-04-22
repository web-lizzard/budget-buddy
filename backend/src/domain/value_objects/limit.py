from dataclasses import dataclass

from domain.exceptions import InvalidLimitValueError

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

    def is_exceeded(self, current_spending: Money) -> bool:
        """
        Check if the limit is exceeded.

        Args:
            current_spending: Current spending as Money object

        Returns:
            True if limit is exceeded, False otherwise

        Raises:
            InvalidLimitValueError: If current_spending is not a Money object
            CurrencyMismatchError: If currencies don't match
        """
        if current_spending.currency != self.value.currency:
            raise InvalidLimitValueError(
                f"Currency mismatch: limit is in {self.value.currency}, spending is in {current_spending.currency}"
            )

        return current_spending.amount > self.value.amount

    def remaining_amount(self, current_spending: Money) -> Money:
        """
        Calculate the remaining amount.

        Args:
            current_spending: Current spending as Money object

        Returns:
            Remaining amount as Money object

        Raises:
            InvalidLimitValueError: If current_spending is not a Money object
            CurrencyMismatchError: If currencies don't match
        """

        if current_spending.currency != self.value.currency:
            raise InvalidLimitValueError(
                f"Currency mismatch: limit is in {self.value.currency}, spending is in {current_spending.currency}"
            )

        if current_spending.amount >= self.value.amount:
            # Return zero money with the same currency if limit is already exceeded
            return Money(0, self.value.currency)

        return Money(self.value.amount - current_spending.amount, self.value.currency)

    def __str__(self) -> str:
        return f"Limit: {self.value}"
