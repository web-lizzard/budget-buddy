from budget.domain import model
from budget.adapters import repository


def test_create_budget(session):
    repo = repository.SQLBudgetRepository(session=session)
    category = model.Category(name="meal")
    budget = model.Budget(categories=[category], _monthly_limit=2000)

    repo.add(budget)

    session.commit()

    assert [budget] == repo.list()


def test_find_categories_by_list_of_ids(session):
    repo = repository.SQLBudgetRepository(session=session)

    category_1 = model.Category(name="meal")
    category_2 = model.Category(name="daily")

    repo.add(category_1)
    repo.add(category_2)

    categories = repo.find_categories_by_ids(
        ids=[str(category_1.id), str(category_2.id)]
    )

    assert len(categories) == 2


def test_find_categories_returns_empty_array_when_uuid_not_passing(session):
    repo = repository.SQLBudgetRepository(session=session)

    categories = repo.find_categories_by_ids(ids=[])

    assert categories == []
