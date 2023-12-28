from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal

import uuid


class CreateProductDTO(BaseModel):
    name: str


class CreateBudgetDTO(BaseModel):
    categories_id: list[str]
    monthly_amount: float

    start_date: datetime | None = None
    end_dat: datetime | None = None

    @field_validator("categories_id")
    @classmethod
    def validate_categories(cls, ids: list[str]):
        for id in ids:
            uuid.UUID(id)
        return ids


class AddExpenseDTO(BaseModel):
    category_id: str
    amount: float
