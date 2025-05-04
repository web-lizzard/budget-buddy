import uuid

from pydantic import AwareDatetime

from .budget_strategy_dto import BudgetStrategyDTO
from .category_dto import CategoryDTO
from .dto import DTO
from .money_dto import MoneyDTO


class BudgetDTO(DTO):
    id: uuid.UUID
    user_id: uuid.UUID
    total_limit: MoneyDTO
    currency: str
    start_date: AwareDatetime
    end_date: AwareDatetime
    strategy: BudgetStrategyDTO
    name: str
    deactivation_date: AwareDatetime | None = None
    categories: list[CategoryDTO] = []
