from abc import ABC
from typing import Protocol

from sqlalchemy.orm import Session

from typing import Any


class Repository(Protocol):
    def get(self) -> None | Any:
        ...

    def list(self) -> list[Any]:
        ...

    def add(self, entity):
        ...


class SQLRepository:
    def __init__(self, session: Session, model) -> None:
        self._model = model
        self._session = session

    def get(self, **kwarg) -> Any | None:
        return self._session.query(self._model).filter_by(**kwarg).first()

    def list(self, criterion=None, join_table=None) -> list[Any]:
        entities = self._session.query(self._model)
        if join_table:
            entities = entities.select_from(join_table)

        if criterion:
            entities.filter(criterion)

        return entities.all()

    def add(self, entity):
        return self._session.add(entity)


class FakeRepository:
    def __init__(self, entities: list) -> None:
        self._entities = set(entities)

    def get(self, id):
        return next(e for e in self._entities if self._entities.id == id)

    def list(self):
        return list(self._entities)

    def add(self, entity):
        self._entities.add(entity)
