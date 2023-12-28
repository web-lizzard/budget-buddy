from fastapi import APIRouter, HTTPException
from fastapi import APIRouter
from budget.domain.model import Budget, Category
from budget.services import services
import dto
from budget.adapters import unit_of_work


router = APIRouter(prefix="/budgets", tags=["budget"])


@router.get("/", response_model=list[Budget])
def get_budgets():
    uow = unit_of_work.SQLBudgetUnitOfWork()
    return services.list_budgets(uow=uow)


@router.post("/", response_model=Budget)
def create_budget(budget_dto: dto.CreateBudgetDTO):
    uow = unit_of_work.SQLBudgetUnitOfWork()

    try:
        budget = services.create_budget(
            uow=uow,
            dto=budget_dto,
        )
        return budget
    except services.CategoriesNotFound as error:
        raise HTTPException(status_code=400, detail=f"{error}")


@router.post(
    "/category",
    response_model=Category,
)
def create_category(category_dto: dto.CreateProductDTO):
    uow = unit_of_work.SQLBudgetUnitOfWork()

    category = services.create_category(dto=category_dto, uow=uow)

    return category


@router.post("/expense", status_code=201)
def expense(dto: dto.AddExpenseDTO):
    uow = unit_of_work.SQLBudgetUnitOfWork()

    try:
        services.associate_expense_to_budgets(
            uow=uow,
            dto=dto,
        )
    except services.CategoriesNotFound as error:
        raise HTTPException(status_code=400, detail=f"{error}")
