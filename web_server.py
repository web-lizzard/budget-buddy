from fastapi import FastAPI, Depends
from db.session import SessionLocal, Base, engine
from pydantic import BaseModel
from sqlalchemy.orm import Session
from budget.orm import BudgetTable, CategoryTable
from budget.model import Category, Budget, Expense, associate_expense
from decimal import Decimal
from datetime import datetime

app = FastAPI()

Base.metadata.create_all(bind=engine)


class CreateCategoryDTO(BaseModel):
    name: str


class CreateBudgetDTO(BaseModel):
    categories_id: list[str]
    limit: float | Decimal

    start_date: datetime | None = None
    end_date: datetime | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/create-category")
def create_category(dto: CreateCategoryDTO, session: Session = Depends(get_db)):
    db_category = CategoryTable(name=dto.name)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)

    return db_category


@app.post("/create-budget")
def create_budget(dto: CreateBudgetDTO, session: Session = Depends(get_db)):
    categories_orm = (
        session.query(CategoryTable)
        .where(CategoryTable.id.in_(id for id in dto.categories_id))
        .all()
    )

    budget = Budget(categories=categories_orm, _monthly_limit=dto.limit)

    session.add(BudgetTable(*budget))

    session.commit()
    session.refresh(budget)

    return budget
