from budget.web_server import router, get_database
from fastapi.testclient import TestClient
from dto import CreateProductDTO, CreateBudgetDTO, AddExpenseDTO
from common.db.session import sessionmaker
from common.db.registry import start_mappers
from common.db.session import metadata
from conftest import override_get_db, engine
import uuid


from web_server import app


metadata.create_all(engine)


client = TestClient(app=app)


def test_create_category():
    app.dependency_overrides[get_database] = override_get_db

    dto = CreateProductDTO(name="test5")

    response = client.post("budgets/category", json=dto.model_dump())

    app.dependency_overrides = {}
    assert response.status_code is 200
    assert response.json()["name"] == "test5"


def test_create_budget():
    app.dependency_overrides[get_database] = override_get_db

    dto = CreateProductDTO(name="test6")

    response = client.post("budgets/category", json=dto.model_dump())

    dto = CreateBudgetDTO(categories_id=[response.json()["id"]], monthly_amount=5000)

    response = client.post("budgets", json=dto.model_dump())

    app.dependency_overrides = {}

    assert response.status_code is 200
    assert "_monthly_limit" in response.json()


def test_add_expense():
    app.dependency_overrides[get_database] = override_get_db

    dto = CreateProductDTO(name="test6")

    response = client.post("budgets/category", json=dto.model_dump())

    category_id = response.json()["id"]

    dto = CreateBudgetDTO(categories_id=[category_id], monthly_amount=5000)

    response = client.post("budgets", json=dto.model_dump())

    dto = AddExpenseDTO(category_id=category_id, amount=300)

    response = client.post("budgets/expense", json=dto.model_dump())

    app.dependency_overrides = {}

    assert response.status_code is 201
