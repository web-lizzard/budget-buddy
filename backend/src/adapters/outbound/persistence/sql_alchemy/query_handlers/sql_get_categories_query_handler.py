from application.dtos import CategoryDTO, CategoryListDTO, MoneyDTO
from application.queries import GetCategoriesQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import BudgetNotFoundError  # For checking budget existence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import BudgetModel, CategoryModel


class SQLGetCategoriesQueryHandler(QueryHandler[GetCategoriesQuery, CategoryListDTO]):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def handle(self, query: GetCategoriesQuery) -> CategoryListDTO:
        # First, check if the budget exists and belongs to the user
        budget_check_stmt = select(BudgetModel.id).where(
            BudgetModel.id == query.budget_id, BudgetModel.user_id == query.user_id
        )
        budget_exists = await self._session.scalar(budget_check_stmt)

        if not budget_exists:
            # Raise BudgetNotFoundError if budget doesn't exist or doesn't belong to user
            raise BudgetNotFoundError(
                f"Budget with id {query.budget_id} not found for user {query.user_id}."
            )

        # If budget exists, fetch categories
        stmt = (
            select(CategoryModel)
            .where(
                CategoryModel.budget_id == query.budget_id,
                # Optionally, re-verify user_id at category level if needed, but checking budget should suffice
                # CategoryModel.user_id == query.user_id
            )
            .order_by(CategoryModel.created_at)
        )

        result = await self._session.scalars(stmt)
        categories = result.all()

        # Map to DTOs
        category_dtos = [
            CategoryDTO(
                id=cat.id,
                name=cat.name,
                limit=MoneyDTO(
                    amount=cat.limit.value.amount, currency=cat.limit.value.currency
                ),
                budget_id=cat.budget_id,
            )
            for cat in categories
        ]

        return CategoryListDTO(categories=category_dtos)
