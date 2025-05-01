from datetime import datetime
from uuid import UUID

from domain.value_objects import Money, TransactionType


class Transaction:
    """
    Aggregate representing a single financial operation.

    Attributes:
        id: Transaction ID
        category_id: Category ID
        amount: Transaction amount
        type: Transaction type (Income/Expense)
        date: Transaction date and time
        description: Optional transaction description
    """

    def __init__(
        self,
        id: UUID,
        category_id: UUID,
        amount: Money,
        transaction_type: TransactionType,
        occurred_date: datetime,
        user_id: UUID,
        description: str | None = None,
    ):
        """Initialize Transaction aggregate.

        Args:
            id: Transaction ID
            category_id: Category ID
            amount: Transaction amount
            transaction_type: Transaction type
            occurred_date: Transaction date and time
            description: Optional transaction description
        """
        self._id = id
        self._category_id = category_id
        self._user_id = user_id
        self._amount = amount
        self._transaction_type = transaction_type
        self._occurred_date = occurred_date
        self._description = description
        self._user_id = user_id

    @property
    def id(self) -> UUID:
        """Get transaction ID."""
        return self._id

    @property
    def category_id(self) -> UUID:
        """Get category ID."""
        return self._category_id

    @property
    def amount(self) -> Money:
        """Get transaction amount."""
        return self._amount

    @property
    def transaction_type(self) -> TransactionType:
        """Get transaction type."""
        return self._transaction_type

    @property
    def occurred_date(self) -> datetime:
        """Get transaction date."""
        return self._occurred_date

    @property
    def description(self) -> str | None:
        """Get transaction description."""
        return self._description

    @property
    def user_id(self) -> UUID:
        """Get user ID."""
        return self._user_id

    def update_category(self, category_id: UUID) -> None:
        """Update the category of the transaction."""
        self._category_id = category_id

    def update(
        self,
        category_id: UUID,
        amount: Money,
        transaction_type: TransactionType,
        occurred_date: datetime,
        description: str | None = None,
    ) -> None:
        """Update transaction details.

        Args:
            category_id: New category ID
            amount: New transaction amount
            transaction_type: New transaction type
            description: New transaction description
        """
        self._category_id = category_id
        self._amount = amount
        self._transaction_type = transaction_type
        self._description = description
        self._occurred_date = occurred_date

    def __str__(self) -> str:
        """String representation of the transaction."""
        return (
            f"Transaction: {self._id}, "
            f"Category: {self._category_id}, "
            f"Amount: {self._amount}, "
            f"Type: {self._transaction_type}, "
            f"Date: {self._occurred_date}, "
            f"Description: {self._description}"
        )
