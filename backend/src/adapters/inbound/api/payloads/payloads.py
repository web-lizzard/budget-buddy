import uuid
from datetime import date, datetime
from enum import Enum
from typing import Literal

from domain.value_objects import BudgetStrategyType
from pydantic import BaseModel, Field


# Local payload definition for Money (used for Budget total_limit)
class MoneyPayload(BaseModel):
    amount: float
    currency: str


# New local payload definition for Amount (used for categories and transactions)
class AmountPayload(BaseModel):
    amount: float


# Local payload definition for Strategy
class StrategyPayload(BaseModel):
    budget_strategy_type: BudgetStrategyType
    parameters: dict = Field(default_factory=dict)


# Local enum for transaction types
class TransactionTypeEnumPayload(str, Enum):
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"


# ----- Budget API Payloads -----


# Payload for creating a new category inside a budget.
class CreateCategoryRequestPayload(BaseModel):
    name: str
    limit: AmountPayload


# Payload for creating a new budget.
class CreateBudgetRequestPayload(BaseModel):
    total_limit: MoneyPayload
    start_date: date
    name: str = Field(..., min_length=3, max_length=100)
    categories: list[CreateCategoryRequestPayload] = Field(default_factory=list)
    strategy: StrategyPayload


# ----- Category API Payloads -----


# Payload for updating an existing category.
class UpdateCategoryRequestPayload(BaseModel):
    name: str
    limit: AmountPayload


# Payload for handling transactions during category deletion (delete option).
class HandleTransactionDeletePayload(BaseModel):
    type: Literal["delete"]


# Payload for handling transactions during category deletion (move option).
class HandleTransactionMovePayload(BaseModel):
    type: Literal["move"]
    target_category_id: uuid.UUID


# Union type for handling transaction during category deletion.
HandleTransactionPayload = HandleTransactionDeletePayload | HandleTransactionMovePayload


# Main payload for deleting a category, including common fields and nested handle_transaction info.
class DeleteCategoryRequestPayload(BaseModel):
    handle_transaction: HandleTransactionPayload


# ----- Transaction API Payloads -----


# Payload for creating a new transaction.
class CreateTransactionRequestPayload(BaseModel):
    category_id: uuid.UUID
    amount: AmountPayload
    transaction_type: TransactionTypeEnumPayload
    description: str | None = None
    occurred_date: datetime


# Payload for updating a transaction.
class UpdateTransactionRequestPayload(BaseModel):
    category_id: uuid.UUID
    amount: AmountPayload
    transaction_type: TransactionTypeEnumPayload
    occurred_date: datetime
    description: str | None = None
