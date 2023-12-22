from db.repository import Repository
from budget.domain.model import Budget, Expense, Category, associate_expense
from sqlalchemy import or_
import dto


class CategoriesNotFound(Exception):
    pass


def create_category(dto: dto.CreateProductDTO, repository: Repository, session):
    category = Category(name=dto.name)
    repository.add(category)

    session.commit()
    return category


def create_budget(
    budget_repository: Repository,
    categories_repository: Repository,
    dto: dto.CreateBudgetDTO,
    session,
):
    categories = categories_repository.list(
        # criterion=or_(*(Category.id == id for id in dto.categories_id))
    )

    if not len(categories):
        raise CategoriesNotFound("Impossible to create budget without categories")

    budget = Budget(categories=categories, _monthly_limit=dto.monthly_amount)
    budget_repository.add(budget)

    session.commit()
    return budget


def associate_expense_to_budgets(
    budget_repository: Repository,
    category_repository: Repository,
    dto: dto.AddExpenseDTO,
    session,
):
    category = category_repository.get(id=dto.category_id)

    if not category:
        raise CategoriesNotFound("Category not found")

    budgets = budget_repository.list(join_table=Category)
    expense = Expense(category=category, _amount=dto.amount)

    associate_expense(expense=expense, budgets=budgets)
    session.commit()
