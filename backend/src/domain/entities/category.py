import uuid
from datetime import datetime
from uuid import UUID

from domain.aggregates.transaction import Transaction
from domain.value_objects.category_name import CategoryName
from domain.value_objects.limit import Limit
from domain.value_objects.money import Money
from domain.value_objects.transaction_type import TransactionType


class Category:
    """
    Entity representing a category within a budget.

    Part of the Budget aggregate, representing an area of spending.
    """

    _id: UUID
    _budget_id: UUID
    _name: CategoryName
    _limit: Limit
    _user_id: UUID

    _MAX_NAME_LENGTH = 255
    _MIN_NAME_LENGTH = 3

    def __init__(
        self,
        id: UUID,
        budget_id: UUID,
        name: CategoryName,
        limit: Limit,
        user_id: UUID | None = None,
    ):
        """
        Initialize a Category entity.

        Args:
            id: Category ID
            budget_id: Budget ID
            name: Category name (string or CategoryName instance)
            limit: Category spending limit

        Raises:
            Various CategoryNameError subclasses if name is invalid
            InvalidLimitValueError if limit is invalid
        """
        self._id = id
        self._budget_id = budget_id
        self._name = name
        self._limit = limit
        self._user_id = user_id or uuid.uuid4()

    @property
    def id(self) -> UUID:
        """Get category ID."""
        return self._id

    @property
    def budget_id(self) -> UUID:
        """Get budget ID."""
        return self._budget_id

    @property
    def name(self) -> CategoryName:
        """Get category name."""
        return self._name

    @property
    def limit(self) -> Limit:
        """Get category limit."""
        return self._limit

    def change_name(self, new_name: CategoryName) -> None:
        """
        Changes the category name.

        Args:
            new_name: New category name (string or CategoryName instance)

        Raises:
            Various CategoryNameError subclasses if name is invalid
        """
        self._name = new_name

    def change_limit(self, new_limit: Limit) -> None:
        """
        Changes the category limit.

        Args:
            new_limit: New category limit

        Raises:
            InvalidLimitValueError: If limit value is negative or invalid type
        """
        self._limit = new_limit

    def create_transaction(
        self,
        id: UUID,
        amount: Money,
        transaction_type: TransactionType,
        occurred_date: datetime,
        user_id: UUID,
        description: str | None = None,
    ) -> Transaction:
        """Create a new transaction for this category.

        Args:
            id: Transaction ID
            amount: Transaction amount
            type: Transaction type
            occurred_date: Transaction date
            user_id: The ID of the user who owns the transaction
            description: Optional transaction description

        Returns:
            Created transaction
        """
        return Transaction(
            id=id,
            category_id=self._id,
            amount=amount,
            transaction_type=transaction_type,
            occurred_date=occurred_date,
            description=description,
            user_id=user_id,
        )

    def __str__(self) -> str:
        return f"Category: {self._name} (ID: {self._id}, Budget: {self._budget_id}), Limit: {self._limit}"
