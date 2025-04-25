import uuid

from .dto import DTO
from .money_dto import MoneyDTO


class CategoryStatisticsRecordDTO(DTO):
    id: uuid.UUID
    category_id: uuid.UUID
    current_balance: MoneyDTO
    daily_available_amount: MoneyDTO
    daily_average: MoneyDTO
    used_limit: MoneyDTO
