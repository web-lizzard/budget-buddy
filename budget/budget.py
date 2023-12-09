from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, field
from monetary.money import Money
from functools import reduce


@dataclass
class Category:
    name: str

    id: str | None = None


@dataclass
class Expense:
    category: Category
    amount: Money
    expense_date: datetime = datetime.now()

    id: str | None = None

    @property
    def amount_int(self):
        return self.amount.current_amount


@dataclass
class Budget:
    monthly_limit: Money
    categories: list[Category]

    expenses: list[Expense] = field(default_factory=list)
    start_date: datetime = datetime.now()
    end_date: datetime = datetime.now() + relativedelta(months=1)
    id: str | None = None

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
    for budget in budgets:
        if expense.category in budget.categories and budget.end_date >= now:
            budget.expenses.append(expense)
