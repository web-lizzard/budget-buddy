from common.db import unit_of_work
from budget.adapters.repository import (
    SQLBudgetRepository,
    BudgetRepository,
    FakeBudgetRepository,
)
from budget.domain import model


class BudgetUnitOfWork(unit_of_work.UnitOfWork):
    repository: BudgetRepository

    def __init__(self) -> None:
        super().__init__()


class SQLBudgetUnitOfWork(BudgetUnitOfWork, unit_of_work.SQLAlchemyUnitOfWork):
    def __enter__(self):
        super().__enter__(model.Budget)
        self.repository = SQLBudgetRepository(self.session)

    def __init__(self) -> None:
        super().__init__()


class FakeBudgetUnitOfWork(BudgetUnitOfWork):
    def __init__(self, categories=[], budgets=[]):
        self.repository = FakeBudgetRepository(entities=budgets, categories=categories)
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
