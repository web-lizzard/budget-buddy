from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from budget.model import Budget, Category, associate_expense, Expense
from db.session import get_session
from db.repository import SQLRepository, Repository
from db.session import get_session, metadata, engine
from db.registry import start_mappers
from budget import services
import dto


app = FastAPI()

metadata.create_all(bind=engine)
start_mappers()


def get_repo(session: Session) -> Repository:
    return SQLRepository(session=session, model=Budget)


def get_database():
    db = get_session()
    try:
        yield get_session()
    finally:
        db.close()


@app.post(
    "/create-category",
    response_model=Category,
)
def create_category(
    category_dto: dto.CreateProductDTO, session: Session = Depends(get_database)
):
    repository = SQLRepository(session=session, model=Category)
    category = services.create_category(
        dto=category_dto, session=session, repository=repository
    )

    return category


@app.post("/create-budget")
def create_budget(budget_dto: dto.CreateBudgetDTO):
    session = get_session()
    budget_repository = SQLRepository(session=session, model=Budget)
    category_repository = SQLRepository(session=session, model=Category)

    budget = services.create_budget(
        budget_repository=budget_repository,
        categories_repository=category_repository,
        dto=budget_dto,
        session=session,
    )

    return budget


@app.post("/add-expense", status_code=201)
def expense(dto: dto.AddExpenseDTO):
    session = get_session()
    budget_repository = SQLRepository(session=session, model=Budget)
    category_repository = SQLRepository(session=session, model=Category)

    services.associate_expense_to_budgets(
        budget_repository=budget_repository,
        category_repository=category_repository,
        session=session,
        dto=dto,
    )
