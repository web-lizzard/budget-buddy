from abc import ABC
from typing import Protocol

from sqlalchemy.orm import Session

from sqlalchemy import select


class Repository(Protocol):
    def get(self, id):
        ...

    def list(self):
        ...

    def add(self):
        ...


class SQLRepository(ABC):
    def __init__(self, session: Session, model) -> None:
        self._model = model
        self._session = session

    def get(self, **kwarg: dict):
        return self._session.query(self._model).filter_by(**kwarg).one()

    def list(self):
        return self._session.query(self._model).all()

    def add(self, entity):
        return self._session.add(entity)

    def find_many_and_join(self, join_table, query):
        return (
            self._session.query(self._model).join(target=join_table).where(query).all()
        )

    def find_many(self, where):
        return self._session.execute(select(self._model).where(where))
