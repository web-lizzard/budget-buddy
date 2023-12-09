from datetime import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, field
from monetary.money import Money
from functools import reduce
from decimal import Decimal
from typing import Sequence


@dataclass
class Category:
    name: str


@dataclass
class Expense:
    category: Category
    _amount: Decimal | float
    expense_date: datetime = datetime.now()

    @property
    def amount(self) -> Money:
        return Money.mint(self._amount)


@dataclass
class Budget:
    categories: Sequence[Category]
    _monthly_limit: float | Decimal

    expenses: list[Expense] = field(default_factory=list)
    start_date: datetime = datetime.now()
    end_date: datetime = datetime.now() + relativedelta(months=1)

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
            budget.expenses.append(expense)
