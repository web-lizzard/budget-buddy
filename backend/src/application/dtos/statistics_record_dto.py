import uuid

from pydantic import AwareDatetime, Field

from .category_statistics_record_dto import CategoryStatisticsRecordDTO
from .dto import DTO
from .money_dto import MoneyDTO


class StatisticsRecordDTO(DTO):
    id: uuid.UUID
    user_id: uuid.UUID
    budget_id: uuid.UUID
    current_balance: MoneyDTO
    daily_available_amount: MoneyDTO
    daily_average: MoneyDTO
    used_limit: MoneyDTO
    creation_date: AwareDatetime
    categories_statistics: list[CategoryStatisticsRecordDTO] = Field(
        default_factory=list
    )
