from budget.adapters.repository import BudgetRepository
from budget.domain.model import Budget, Expense, Category, associate_expense
import dto


class CategoriesNotFound(Exception):
    pass


def create_category(dto: dto.CreateProductDTO, repository: BudgetRepository, session):
    category = Category(name=dto.name)
    repository.add(category)

    session.commit()
    return category


def create_budget(
    budget_repository: BudgetRepository,
    dto: dto.CreateBudgetDTO,
    session,
):
    categories = budget_repository.find_categories_by_ids(dto.categories_id)

    if not len(categories):
        raise CategoriesNotFound("Impossible to create budget without categories")

    budget = Budget(categories=categories, _monthly_limit=dto.monthly_amount)
    budget_repository.add(budget)

    session.commit()
    return budget


def associate_expense_to_budgets(
    budget_repository: BudgetRepository,
    dto: dto.AddExpenseDTO,
    session,
):
    category = budget_repository.find_category(id=dto.category_id)

    if not category:
        raise CategoriesNotFound("Category not found")

    budgets = budget_repository.list(join_table=Category)
    expense = Expense(category=category, _amount=dto.amount)

    associate_expense(expense=expense, budgets=budgets)
    session.commit()
