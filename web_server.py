from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, select
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


def get_database():
    start_mappers()
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


@app.post(
    "/create-category",
    response_model=Category,
)
def create_category(
    category_dto: CreateProductDTO, session: Session = Depends(get_database)
):
    print(category_dto)
    category = Category(name=category_dto.name)
    repository = SQLRepository(session=session, model=Category)

    repository.add(category)

    session.commit()

    session.refresh(category)

    print(repository.list())

    return category


@app.post("/create-budget", response_model=Budget)
def create_budget(budget_dto: CreateBudgetDTO):
    session = get_session()
    budget_repository = SQLRepository(session=session, model=Budget)
    category_repository = SQLRepository(session=session, model=Category)

    stm = select(Category).where(Category.name == "Meal")

    categories = session.execute(stm).all()
    budget = Budget(
        monthly_limit=Money.mint(budget_dto.monthly_amount), categories=categories
    )

    budget_repository.add(budget)

    session.commit()

    return budget


@app.post("/add-expense", response_model=list[Budget])
def expense():
    session = get_session()
    category = Category(name="Meal")
    budget = Budget(monthly_limit=Money.mint(40000), categories=[category])
    expense = Expense(category=category, amount=Money.mint(400))

    associate_expense(expense=expense, budgets=[budget])

    session.add(budget)

    session.commit()

    data = session.query(Budget).all()

    return data
