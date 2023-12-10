from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, select, any_
from pydantic import BaseModel
from budget.budget import Budget, Category, associate_expense, Expense
from monetary.money import Money
from db.session import get_session
from db.repository import SQLRepository
from datetime import datetime
from decimal import Decimal
from db.session import get_session
from db.model import start_mappers

app = FastAPI()

start_mappers()


def get_database():
    db = get_session()
    try:
        yield get_session()
    finally:
        db.close()


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


@app.post(
    "/create-category",
    response_model=Category,
)
def create_category(
    category_dto: CreateProductDTO, session: Session = Depends(get_database)
):
    category = Category(name=category_dto.name)
    repository = SQLRepository(session=session, model=Category)

    repository.add(category)

    session.commit()

    return category


@app.post("/create-budget")
def create_budget(budget_dto: CreateBudgetDTO):
    session = get_session()

    categories = (
        session.query(Category)
        .filter(or_(*(Category.id == id for id in budget_dto.categories_id)))
        .all()
    )

    budget = Budget(_monthly_limit=budget_dto.monthly_amount, categories=categories)

    session.add(budget)
    session.commit()

    return budget


@app.post("/add-expense")
def expense(dto: AddExpenseDTO):
    session = get_session()

    category = session.query(Category).filter_by(id=dto.category_id).first()
    budgets = session.query(Budget).select_from(Category).all()
    expense = Expense(category=category, _amount=dto.amount)

    associate_expense(expense=expense, budgets=budgets)

    session.commit()
