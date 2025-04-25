from typing import Generic, TypeVar

from .dto import DTO

T = TypeVar("T", bound=DTO)


class PaginatedItemDTO(DTO, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
