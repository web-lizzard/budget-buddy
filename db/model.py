from sqlalchemy.orm import registry, relationship
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    MetaData,
    BINARY,
    create_engine,
    Uuid,
)
from budget.budget import Budget, Category, Expense
from uuid import uuid4
from settings import settings


mapper_registry = registry()
metadata = MetaData()

engine = create_engine(settings.database.url)


def _create_uuid():
    return uuid4()


category_table = Table(
    "categories",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False),
    Column("name", String(length=100)),
)


expense_table = Table(
    "expenses",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, default=_create_uuid),
    Column("amount_int", Integer),
    Column("expense_date", DateTime),
    Column("category_id", ForeignKey("categories.id")),
)


budget_table = Table(
    "budgets",
    metadata,
    Column(
        "id", Uuid(as_uuid=True), primary_key=True, unique=True, default=_create_uuid
    ),
    Column("limit", Integer),
    Column("start_date", DateTime),
    Column("end_date", DateTime),
)

budget_category_association_table = Table(
    "budget_category_association_table",
    metadata,
    Column("budget_id", ForeignKey("budgets.id"), primary_key=True),
    Column("category_id", ForeignKey("categories.id"), primary_key=True),
)

budget_expense_association_table = Table(
    "budget_expense_association_table",
    metadata,
    Column("budget_id", ForeignKey("budgets.id"), primary_key=True),
    Column("expense_id", ForeignKey("expenses.id"), primary_key=True),
)


def start_mappers():
    category_mapper = mapper_registry.map_imperatively(Category, category_table)

    expense_mapper = mapper_registry.map_imperatively(Expense, expense_table)
    budget_mapper = mapper_registry.map_imperatively(
        Budget,
        budget_table,
        properties={
            "expenses": relationship(
                expense_mapper,
                secondary=budget_expense_association_table,
                collection_class=list,
            ),
            "categories": relationship(
                category_mapper,
                secondary=budget_category_association_table,
                collection_class=list,
            ),
        },
    )
