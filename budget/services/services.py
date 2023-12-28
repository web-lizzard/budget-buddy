from budget.adapters.repository import BudgetRepository
from budget.adapters.unit_of_work import BudgetUnitOfWork
from budget.domain.model import Budget, Expense, Category, associate_expense
import dto
from common.db import unit_of_work


class CategoriesNotFound(Exception):
    pass


def create_category(dto: dto.CreateProductDTO, uow: BudgetUnitOfWork):
    category = Category(name=dto.name)

    with uow:
        uow.repository.add(category)
        uow.commit()

    return category


def create_budget(
    uow: BudgetUnitOfWork,
    dto: dto.CreateBudgetDTO,
):
    with uow:
        categories = uow.repository.find_categories_by_ids(dto.categories_id)

        if not len(categories):
            raise CategoriesNotFound("Impossible to create budget without categories")

        budget = Budget(categories=categories, _monthly_limit=dto.monthly_amount)
        uow.repository.add(budget)

        uow.commit()
    return budget


def associate_expense_to_budgets(
    uow: BudgetUnitOfWork,
    dto: dto.AddExpenseDTO,
):
    with uow:
        category = uow.repository.find_category(id=dto.category_id)

        if not category:
            raise CategoriesNotFound("Category not found")

        budgets = uow.repository.list(join_table=Category)
        expense = Expense(category=category, _amount=dto.amount)

        associate_expense(expense=expense, budgets=budgets)
        uow.commit()


def list_budgets(uow: BudgetUnitOfWork):
    with uow:
        return uow.repository.list()
