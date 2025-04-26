from enum import Enum


class TransactionType(Enum):
    """Enum representing transaction types."""

    EXPENSE = "EXPENSE"
    INCOME = "INCOME"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "TransactionType":
        """
        Create TransactionType from string.

        Args:
            value: String representation of transaction type

        Returns:
            TransactionType enum value

        Raises:
            ValueError: If value is not a valid transaction type
        """
        try:
            return cls(value.upper())
        except ValueError:
            valid_types = ", ".join([t.value for t in cls])
            raise ValueError(
                f"Invalid transaction type: {value}. Valid types are: {valid_types}"
            )
