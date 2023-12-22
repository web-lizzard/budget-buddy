from typing import Protocol

from sqlalchemy.orm import Session

from typing import Any


class Repository(Protocol):
    def get(self, **kwargs) -> Any | None:
        ...

    def list(self, **kwargs) -> list[Any]:
        ...

    def add(self, entity):
        ...


class SQLRepository:
    def __init__(self, session: Session, model) -> None:
        self._model = model
        self._session = session

    def get(self, **kwarg) -> Any | None:
        item = self._session.query(self._model).filter_by(**kwarg).first()

        return item

    def list(self, **kwargs) -> list[Any]:
        join_table = kwargs.get("join_table")
        criterion = kwargs.get("criterion")
        entities = self._session.query(self._model)
        if join_table:
            entities = entities.select_from(join_table)

        if criterion:
            entities = entities.filter(criterion)

        return entities.all()

    def add(self, entity):
        return self._session.add(entity)


class FakeRepository:
    def __init__(self, entities: list) -> None:
        self._entities = entities

    def get(self, **kwargs):
        try:
            return next(e for e in self._entities if str(e.id) == kwargs["id"])
        except StopIteration:
            return None

    def list(self, **kwargs):
        return list(self._entities)

    def add(self, entity):
        self._entities.append(entity)
