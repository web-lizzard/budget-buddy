import uuid

from .dto import DTO
from .money_dto import MoneyDTO


class CategoryDTO(DTO):
    id: uuid.UUID
    budget_id: uuid.UUID
    name: str
    limit: MoneyDTO
