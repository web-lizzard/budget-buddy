from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from budget.model import Budget, Category, associate_expense, Expense
from db.session import get_session
from db.repository import SQLRepository, Repository
from datetime import datetime
from decimal import Decimal
from db.session import get_session
from db.registry import start_mappers

app = FastAPI()

start_mappers()


def get_repo(session: Session) -> Repository:
    return SQLRepository(session=session, model=Budget)


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
    budget_repository = SQLRepository(session=session, model=Budget)
    category_repository = SQLRepository(session=session, model=Category)

    categories = category_repository.list(
        criterion=or_(*(Category.id == id for id in budget_dto.categories_id))
    )
    budget = Budget(_monthly_limit=budget_dto.monthly_amount, categories=categories)

    budget_repository.add(budget)
    session.commit()

    return budget


@app.post("/add-expense", status_code=201)
def expense(dto: AddExpenseDTO):
    session = get_session()
    budget_repository = SQLRepository(session=session, model=Budget)
    category_repository = SQLRepository(session=session, model=Category)

    category = category_repository.get(id=dto.category_id)
    budgets = budget_repository.list(join_table=Category)
    expense = Expense(category=category, _amount=dto.amount)

    associate_expense(expense=expense, budgets=budgets)
    session.commit()
