from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from application.dtos import DTO
from application.queries import Query

# Define a type variable bound to Query
TQuery = TypeVar("TQuery", bound=Query)
TDTO = TypeVar("TDTO", bound=DTO)


class QueryHandler(Generic[TQuery, TDTO], ABC):
    @property
    def query_name(self) -> str:
        return self.__class__.__name__.replace("Handler", "").lower().replace("_", "")

    @abstractmethod
    async def handle(self, query: TQuery) -> TDTO: ...
