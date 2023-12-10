from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, field
from monetary.money import Money
from functools import reduce
from decimal import Decimal
from uuid import uuid4, UUID


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
    def amount(self):
        return Money.mint(self._amount)


@dataclass
class Budget:
    categories: list[Category]

    _monthly_limit: float | Decimal

    expenses: list[Expense] = field(default_factory=list)
    start_date: datetime = datetime.now()
    end_date: datetime = datetime.now() + relativedelta(months=1)
    id: UUID = field(default_factory=uuid4)

    @property
    def monthly_limit(self) -> Money:
        return Money.mint(self._monthly_limit)

    @property
    def current_balance(self) -> Money:
        return self.monthly_limit - self.computed_expenses

    @property
    def computed_expenses(self) -> Money:
        return reduce(lambda a, b: a + b.amount, self.expenses, Money.mint(0))

    @property
    def limit(self) -> int:
        return self.monthly_limit.current_amount


def associate_expense(expense: Expense, budgets: list[Budget]):
    now = datetime.now()
    print(expense)
    for budget in budgets:
        if expense.category in budget.categories and budget.end_date >= now:
            budget.expenses.append(expense)
            print("eh")
