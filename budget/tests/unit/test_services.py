from budget.domain.model import Budget, Category
import dto
from budget.adapters import unit_of_work as unit_of_work
from budget.services import services
import pytest


def test_list_budget():
    category = Category(name="test-category")
    budget = Budget(categories=[category], _monthly_limit=3000)
    uow = unit_of_work.FakeBudgetUnitOfWork(categories=[category], budgets=[budget])

    budgets = services.list_budgets(uow=uow)
    assert budgets == [budget]


def test_list_expenses():
    category = Category(name="test-category")
    budget = Budget(categories=[category], _monthly_limit=3000)
    uow = unit_of_work.FakeBudgetUnitOfWork(categories=[category], budgets=[budget])


def test_create_category():
    uow = unit_of_work.FakeBudgetUnitOfWork()

    category = services.create_category(dto=dto.CreateProductDTO(name="Meal"), uow=uow)

    assert [category] == uow.repository.list()


def test_budget_creation():
    category = Category(name="Meal")
    uow = unit_of_work.FakeBudgetUnitOfWork(categories=[category], budgets=[])

    budget = services.create_budget(
        dto=dto.CreateBudgetDTO(categories_id=[str(category.id)], monthly_amount=2000),
        uow=uow,
    )

    assert uow.repository.list() == [budget]
    assert uow.committed == True


def test_error_empty_categories():
    uow = unit_of_work.FakeBudgetUnitOfWork()

    with pytest.raises(services.CategoriesNotFound):
        services.create_budget(
            dto=dto.CreateBudgetDTO(categories_id=[], monthly_amount=2000), uow=uow
        )


def test_associate_expense():
    category = Category(name="Meal")
    budget = Budget(categories=[category], _monthly_limit=3000)
    uow = unit_of_work.FakeBudgetUnitOfWork(budgets=[budget], categories=[category])

    services.associate_expense_to_budgets(
        uow=uow,
        dto=dto.AddExpenseDTO(category_id=str(category.id), amount=400),
    )

    assert uow.committed == True


def test_error_not_category():
    category = Category(name="Meal")
    budget = Budget(categories=[], _monthly_limit=3000)
    uow = unit_of_work.FakeBudgetUnitOfWork(budgets=[budget])

    with pytest.raises(services.CategoriesNotFound, match="Category not found"):
        services.associate_expense_to_budgets(
            uow=uow,
            dto=dto.AddExpenseDTO(category_id=str(category.id), amount=400),
        )
