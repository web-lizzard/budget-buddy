from datetime import datetime
from dataclasses import dataclass, field
from monetary.money import Money
from functools import reduce


@dataclass
class Category:
    name: str


@dataclass
class Expense:
    category: Category
    amount: Money
    expense_date: datetime = datetime.now()


@dataclass
class Budget:
    monthly_limit: Money
    end_date: datetime
    categories: list[Category]

    expenses: list[Expense] = field(default_factory=list)
    start_date: datetime = datetime.now()

    @property
    def current_balance(self) -> Money:
        return self.monthly_limit - self.computed_expenses

    @property
    def computed_expenses(self) -> Money:
        return reduce(lambda a, b: a + b.amount, self.expenses, Money.mint(0))


def associate_expense(expense: Expense, budgets: list[Budget]):
    for budget in budgets:
        if expense.category in budget.categories:
            budget.expenses.append(expense)
