from fastapi import APIRouter, HTTPException
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from budget.domain.model import Budget, Category
from budget.adapters.repository import SQLBudgetRepository
from common.db.session import get_database
from budget.services import services
import dto

router = APIRouter(prefix="/budgets", tags=["budget"])


@router.post("/", response_model=Budget)
def create_budget(
    budget_dto: dto.CreateBudgetDTO, session: Session = Depends(get_database)
):
    budget_repository = SQLBudgetRepository(session=session)

    try:
        budget = services.create_budget(
            budget_repository=budget_repository,
            dto=budget_dto,
            session=session,
        )

        return budget
    except services.CategoriesNotFound as error:
        raise HTTPException(status_code=400, detail=f"{error}")


@router.post(
    "/category",
    response_model=Category,
)
def create_category(
    category_dto: dto.CreateProductDTO, session: Session = Depends(get_database)
):
    repository = SQLBudgetRepository(session=session)
    category = services.create_category(
        dto=category_dto, session=session, repository=repository
    )

    return category


@router.post("/expense", status_code=201)
def expense(dto: dto.AddExpenseDTO, session: Session = Depends(get_database)):
    budget_repository = SQLBudgetRepository(session=session)

    try:
        services.associate_expense_to_budgets(
            budget_repository=budget_repository,
            session=session,
            dto=dto,
        )
    except services.CategoriesNotFound as error:
        raise HTTPException(status_code=400, detail=f"{error}")
