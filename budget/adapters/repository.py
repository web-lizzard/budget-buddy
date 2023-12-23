from budget.domain import model
from common.db.repository import Repository, SQLRepository, FakeRepository
from abc import abstractmethod
from sqlalchemy import or_, select, false


class BudgetRepository(Repository):
    @abstractmethod
    def find_categories_by_ids(self, ids: list[str]) -> list[model.Category]:
        pass

    @abstractmethod
    def find_category(self, id) -> model.Category | None:
        pass


class SQLBudgetRepository(SQLRepository, BudgetRepository):
    def find_categories_by_ids(self, ids: list[str]):
        statement = select(model.Category).where(
            or_(*(model.Category.id == id for id in ids), false())
        )
        return self._session.scalars(statement=statement).all()

    def find_category(self, id):
        return self._session.query(model.Category).filter_by(id=id).first()


class FakeBudgetRepository(FakeRepository, BudgetRepository):
    def __init__(self, entities: list, categories: list) -> None:
        super().__init__(entities)
        self._categories = categories

    def find_categories_by_ids(self, ids: list[str]) -> list[model.Category]:
        return [item for item in self._categories if item.id in ids]

    def find_category(self, id) -> model.Category | None:
        try:
            return next(e for e in self._categories if str(e.id) == id)
        except StopIteration:
            return None
