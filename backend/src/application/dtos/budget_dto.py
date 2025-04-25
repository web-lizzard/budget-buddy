import uuid
from datetime import date, datetime

from .budget_strategy_dto import BudgetStrategyDTO
from .category_dto import CategoryDTO
from .dto import DTO
from .money_dto import MoneyDTO


class BudgetDTO(DTO):
    id: uuid.UUID
    user_id: uuid.UUID
    total_limit: MoneyDTO
    currency: str
    start_date: date
    end_date: date
    strategy: BudgetStrategyDTO
    name: str
    deactivation_date: datetime | None = None
    categories: list[CategoryDTO] = []
