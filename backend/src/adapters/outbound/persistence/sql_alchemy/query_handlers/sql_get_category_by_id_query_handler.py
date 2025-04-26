from application.dtos import CategoryDTO, MoneyDTO
from application.queries import GetCategoryByIdQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import CategoryNotFoundError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import CategoryModel


class SQLGetCategoryByIdQueryHandler(QueryHandler[GetCategoryByIdQuery, CategoryDTO]):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def handle(self, query: GetCategoryByIdQuery) -> CategoryDTO:
        stmt = select(CategoryModel).where(
            CategoryModel.id == query.category_id,
            CategoryModel.budget_id == query.budget_id,
            # Add user_id check here
            CategoryModel.user_id == query.user_id,
        )

        result = await self._session.scalar(stmt)

        if not result:
            # If category doesn't exist or user_id doesn't match, raise error
            raise CategoryNotFoundError(
                f"Category with id {query.category_id} not found for budget {query.budget_id} and user {query.user_id}."
            )

        return CategoryDTO(
            id=result.id,
            name=result.name,
            limit=MoneyDTO(
                amount=result.limit.value.amount, currency=result.limit.value.currency
            ),
            budget_id=result.budget_id,
        )
