from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from application.dtos.dtos import DTO
from application.queries.query import Query

# Define a type variable bound to Query
TQuery = TypeVar("TQuery", bound=Query)


class QueryHandler(Generic[TQuery], ABC):
    @property
    def query_name(self) -> str:
        return self.__class__.__name__.replace("Handler", "").lower().replace("_", "")

    @abstractmethod
    async def handle(self, query: TQuery) -> DTO: ...
