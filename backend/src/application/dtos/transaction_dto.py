import uuid
from datetime import datetime
from enum import Enum

from .dto import DTO
from .money_dto import MoneyDTO


class TransactionTypeEnum(Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TransactionDTO(DTO):
    id: uuid.UUID
    category_id: uuid.UUID
    amount: MoneyDTO
    transaction_type: TransactionTypeEnum
    occurred_date: datetime
    description: str | None = None
    user_id: uuid.UUID
