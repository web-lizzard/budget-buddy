from fastapi import APIRouter
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from budget.domain.model import Budget, Category
from db.session import get_session
from db.repository import SQLRepository, Repository
from db.session import get_session
from budget.services import services
import dto

router = APIRouter(prefix="/budgets")


def get_repo(session: Session) -> Repository:
    return SQLRepository(session=session, model=Budget)


def get_database():
    db = get_session()
    try:
        yield get_session()
    finally:
        db.close()


@router.post(
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


@router.post("/create-budget")
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


@router.post("/add-expense", status_code=201)
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
