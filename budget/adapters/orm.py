from sqlalchemy import (
    Table,
    Column,
    DECIMAL,
    String,
    ForeignKey,
    DateTime,
    Uuid,
)
from sqlalchemy.orm import relationship
from budget.domain.model import Budget, Category, Expense
from common.db.session import metadata, mapper_registry


category_table = Table(
    "categories",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, unique=True, nullable=False),
    Column("name", String(length=100)),
)


expense_table = Table(
    "expenses",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, unique=True, nullable=False),
    Column("expense_date", DateTime),
    Column("category_id", ForeignKey("categories.id")),
    Column("_amount", DECIMAL),
)


budget_table = Table(
    "budgets",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, unique=True, nullable=False),
    Column("start_date", DateTime),
    Column("end_date", DateTime),
    Column("_monthly_limit", DECIMAL),
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

    expense_mapper = mapper_registry.map_imperatively(
        Expense,
        expense_table,
        properties={"category": relationship(category_mapper)},
    )
    mapper_registry.map_imperatively(
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
