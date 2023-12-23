from datetime import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, field
from common.monetary.money import Money
from functools import reduce
from decimal import Decimal
from uuid import uuid4, UUID


def get_relative_delta(**kwargs):
    return relativedelta(**kwargs)


@dataclass
class Category:
    name: str

    id: UUID = field(default_factory=uuid4)


@dataclass
class Expense:
    category: Category
    _amount: float | Decimal

    expense_date: datetime = datetime.now()
    id: UUID = field(default_factory=uuid4)

    @property
    def amount(self) -> Money:
        return Money.mint(self._amount)


@dataclass
class Budget:
    categories: list[Category]
    _monthly_limit: float | Decimal

    _monthly_limit: float | Decimal

    id: UUID = field(default_factory=uuid4)
    expenses: list[Expense] = field(default_factory=list)
    end_date: datetime = datetime.now() + get_relative_delta(months=1)
    start_date: datetime = datetime.now()

    @property
    def monthly_limit(self) -> Money:
        return Money.mint(self._monthly_limit)

    @property
    def current_balance(self) -> Money:
        return self.monthly_limit - self.computed_expenses

    @property
    def computed_expenses(self) -> Money:
        return reduce(lambda a, b: a + b.amount, self.expenses, Money.mint(0))


def associate_expense(expense: Expense, budgets: list[Budget]):
    for budget in budgets:
        if (
            expense.category in budget.categories
            and budget.end_date >= expense.expense_date
        ):
            print("expense", expense)
            budget.expenses.append(expense)
