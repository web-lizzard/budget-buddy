import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class DTO(BaseModel):
    pass


class MoneyDTO(DTO):
    amount: int
    currency: str


class BudgetStrategyDTO(DTO):
    type: str  # e.g., 'monthly' or 'yearly'
    parameters: dict = Field(default_factory=dict)


class CategoryDTO(DTO):
    id: uuid.UUID
    budget_id: uuid.UUID
    name: str
    limit: MoneyDTO


# DTO for budget aggregate.
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


# Enum for transaction types.
class TransactionTypeEnum(str, Enum):
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"


# DTO for transaction aggregate.
class TransactionDTO(DTO):
    id: uuid.UUID
    category_id: uuid.UUID
    amount: MoneyDTO
    transaction_type: TransactionTypeEnum
    occurred_date: datetime
    description: str | None = None
    user_id: uuid.UUID


# DTO for statistics record for a category.
class CategoryStatisticsRecordDTO(DTO):
    id: uuid.UUID
    category_id: uuid.UUID
    current_balance: MoneyDTO
    daily_available_amount: MoneyDTO
    daily_average: MoneyDTO
    used_limit: MoneyDTO


# DTO for overall statistics record.
class StatisticsRecordDTO(DTO):
    id: uuid.UUID
    user_id: uuid.UUID
    budget_id: uuid.UUID
    current_balance: MoneyDTO
    daily_available_amount: MoneyDTO
    daily_average: MoneyDTO
    used_limit: MoneyDTO
    creation_date: datetime
    categories_statistics: list[CategoryStatisticsRecordDTO] = Field(
        default_factory=list
    )
