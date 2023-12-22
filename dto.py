from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class CreateProductDTO(BaseModel):
    name: str


class CreateBudgetDTO(BaseModel):
    categories_id: list[str]
    monthly_amount: float | Decimal

    start_date: datetime | None = None
    end_dat: datetime | None = None


class AddExpenseDTO(BaseModel):
    category_id: str
    amount: float | Decimal
