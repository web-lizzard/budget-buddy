from datetime import datetime
from functools import reduce
from typing import List, Optional
from uuid import UUID, uuid4

from domain.entities.category import Category
from domain.exceptions import (
    CannotAddTransactionToDeactivatedBudgetError,
    CategoryLimitExceedsBudgetError,
    CategoryNotFoundError,
    CurrencyMismatchError,
    DuplicateCategoryNameError,
    MaxCategoriesReachedError,
    TransactionOutsideBudgetPeriodError,
)
from domain.value_objects import CategoryName, Limit, Money
from domain.value_objects.budget_strategy import BudgetStrategyInput


class Budget:
    """
    Aggregate representing a user's financial plan for a specified period.
    """

    _id: UUID
    _user_id: UUID
    _total_limit: Limit
    _currency: str
    _start_date: datetime
    _end_date: datetime
    _deactivation_date: datetime | None
    _categories: list[Category]

    _MAX_CATEGORIES = 5

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        total_limit: Limit,
        start_date: datetime,
        end_date: datetime,
        strategy_input: BudgetStrategyInput,
        categories: list[Category] | None = None,
        deactivation_date: datetime | None = None,
    ):
        """
        Initialize a Budget aggregate.

        Args:
            id: Budget ID
            user_id: User ID
            total_limit: Total budget limit
            start_date: Budget start date
            end_date: Budget end date
            deactivation_date: Budget deactivation date (optional)
            categories: List of categories (optional)
        """
        self._id = id
        self._user_id = user_id
        self._total_limit = total_limit
        self._currency = total_limit.value.currency
        self._start_date = start_date
        self._end_date = end_date
        self._deactivation_date = deactivation_date
        self._categories = categories or []
        self._strategy_input = strategy_input

    @property
    def id(self) -> UUID:
        """Get budget ID."""
        return self._id

    @property
    def user_id(self) -> UUID:
        """Get user ID."""
        return self._user_id

    @property
    def total_limit(self) -> Limit:
        """Get total budget limit."""
        return self._total_limit

    @property
    def currency(self) -> str:
        """Get budget currency."""
        return self._currency

    @property
    def start_date(self) -> datetime:
        """Get budget start date."""
        return self._start_date

    @property
    def end_date(self) -> datetime:
        """Get budget end date."""
        return self._end_date

    @property
    def deactivation_date(self) -> Optional[datetime]:
        """Get budget deactivation date."""
        return self._deactivation_date

    @property
    def categories(self) -> List[Category]:
        """Get budget categories."""
        return self._categories

    @property
    def is_active(self) -> bool:
        """Check if budget is active."""
        return self._deactivation_date is None

    @property
    def strategy_input(self) -> BudgetStrategyInput:
        return self._strategy_input

    def add_category(self, name: CategoryName, limit: Limit) -> Category:
        """
        Add a new category to the budget.

        Args:
            name: Category name
            limit: Category limit

        Returns:
            The newly created Category

        Raises:
            MaxCategoriesReachedError: If maximum number of categories is reached
            DuplicateCategoryNameError: If category with the same name already exists
            CategoryLimitExceedsBudgetError: If category limit exceeds available budget limit
        """
        if len(self._categories) >= self._MAX_CATEGORIES:
            raise MaxCategoriesReachedError(self._MAX_CATEGORIES)

        for category in self._categories:
            if category.name.value.lower() == name.value.lower():
                raise DuplicateCategoryNameError(name.value)

        if self.total_limit.is_exceeded(self._calculate_used_limit(limit)):
            raise CategoryLimitExceedsBudgetError(
                name.value, str(limit.value), str(self.total_limit.value)
            )

        category_id = uuid4()
        category = Category(id=category_id, budget_id=self._id, name=name, limit=limit)

        self._categories.append(category)
        return category

    def remove_category(self, category_id: UUID) -> None:
        """
        Remove a category from the budget.

        Args:
            category_id: ID of the category to remove
        """
        self._categories = [c for c in self._categories if c.id != category_id]

    def edit_category(
        self,
        category_id: UUID,
        name: CategoryName | None = None,
        limit: Limit | None = None,
    ) -> Category:
        """
        Edit a category in the budget.

        Args:
            category_id: ID of the category to edit
            name: New name for the category (optional)
            limit: New limit for the category (optional)

        Returns:
            The edited Category

        Raises:
            CategoryNotFoundError: If the category to edit does not exist in the budget.
            DuplicateCategoryNameError: If another category with the same name already exists.
            CategoryLimitExceedsBudgetError: If the new limit exceeds the available budget limit.
        """
        # Find the existing category by id
        existing_category = next(
            (c for c in self._categories if c.id == category_id), None
        )
        if existing_category is None:
            raise CategoryNotFoundError(str(category_id))

        if name is not None:
            for c in self._categories:
                if c.id != category_id and c.name.value.lower() == name.value.lower():
                    raise DuplicateCategoryNameError(name.value)

            existing_category.change_name(name)

        if limit is not None:
            used_limit = self._calculate_used_limit(
                limit, exclude_category_id=category_id
            )
            if self.total_limit.is_exceeded(used_limit):
                raise CategoryLimitExceedsBudgetError(
                    name.value if name else existing_category.name.value,
                    str(limit.value),
                    str(self.total_limit.value),
                )
            existing_category.change_limit(limit)

        return existing_category

    def deactivate_budget(self) -> None:
        """Deactivate the budget."""
        if self._deactivation_date is None:
            self._deactivation_date = datetime.now()

    def validate_transaction_date(self, transaction_date: datetime) -> None:
        """Validate if transaction date is within budget period.

        Args:
            transaction_date: Transaction date to validate

        Raises:
            TransactionDateError: When transaction date is not within budget period
            DeactivatedBudgetError: When budget is deactivated and transaction date is after deactivation date
        """
        # Check if transaction date is within budget period
        if transaction_date < self._start_date or transaction_date > self._end_date:
            raise TransactionOutsideBudgetPeriodError()

        # Check if budget is deactivated and transaction date is after deactivation
        if self._deactivation_date and transaction_date > self._deactivation_date:
            raise CannotAddTransactionToDeactivatedBudgetError(
                str(transaction_date), str(self._deactivation_date)
            )

    def validate_transaction_currency(self, currency: str) -> None:
        """
        Validate transaction currency against budget currency.

        Args:
            currency: Transaction currency

        Raises:
            CurrencyMismatchError: If transaction currency doesn't match budget currency
        """
        if currency != self._currency:
            raise CurrencyMismatchError(currency, self._currency)

    def get_category_by(self, category_id: UUID) -> Category:
        """Get category by id.

        Args:
            category_id: The ID of the category to find

        Returns:
            Category if found

        Raises:
            CategoryNotFoundError: When category is not found in this budget
        """
        category = next((c for c in self._categories if c.id == category_id), None)
        print(f"Category: {category}")
        if category is None:
            raise CategoryNotFoundError(str(category_id))
        return category

    def _calculate_used_limit(
        self, limit: Limit, exclude_category_id: UUID | None = None
    ) -> Limit:
        """
        Calculate the total limit used by all categories.

        Returns:
            Total limit used in smallest currency units (e.g., cents)
        """
        amount = reduce(
            lambda acc, category: (
                acc.add(category.limit.value)
                if category.id != exclude_category_id
                else acc
            ),
            self._categories,
            Money(0, self._currency),
        )
        return Limit(value=amount.add(limit.value))

    def __str__(self) -> str:
        return (
            f"Budget: {self._id}, "
            f"User: {self._user_id}, "
            f"Limit: {self._total_limit}, "
            f"Period: {self._start_date} to {self._end_date}, "
            f"Active: {self.is_active}, "
            f"Categories: {len(self._categories)}"
        )

    def _validate_category_name_uniqueness(self, name: CategoryName) -> None:
        """
        Validate that the category name is unique within the budget.

        Args:
            name: The name of the category to check.

        Raises:
            DuplicateCategoryNameError: If a category with the same name already exists.
        """
        for category in self._categories:
            if category.name.value.lower() == name.value.lower():
                raise DuplicateCategoryNameError(name.value)

    def _validate_category_limit(self, name: CategoryName, limit: Limit) -> None:
        """
        Validate that the category limit does not exceed the total budget limit.

        Args:
            name: The name of the category being validated.
            limit: The limit to validate.

        Raises:
            CategoryLimitExceedsBudgetError: If the category limit exceeds the available budget limit.
        """
        if self.total_limit.is_exceeded(self._calculate_used_limit(limit)):
            raise CategoryLimitExceedsBudgetError(
                name.value, str(limit.value), str(self.total_limit.value)
            )
