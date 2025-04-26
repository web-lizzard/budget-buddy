from application.dtos import MoneyDTO, TransactionDTO, TransactionTypeEnum
from application.queries import GetTransactionByIdQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import TransactionNotFoundError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import TransactionModel


class SQLGetTransactionByIdQueryHandler(
    QueryHandler[GetTransactionByIdQuery, TransactionDTO]
):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def handle(self, query: GetTransactionByIdQuery) -> TransactionDTO:
        stmt = select(TransactionModel).where(
            TransactionModel.id == query.transaction_id,
            # TransactionModel.category.has(budget_id=query.budget_id), # Need to check budget indirectly if needed
            TransactionModel.user_id == query.user_id,  # Direct user_id check
        )

        result = await self._session.scalar(stmt)

        if not result:
            # If transaction doesn't exist or user_id doesn't match, raise error
            raise TransactionNotFoundError(
                f"Transaction with id {query.transaction_id} not found for user {query.user_id}."
            )

        return TransactionDTO(
            id=result.id,
            category_id=result.category_id,
            amount=MoneyDTO(
                amount=result.amount.amount, currency=result.amount.currency
            ),
            transaction_type=TransactionTypeEnum(result.transaction_type.value),
            occurred_date=result.occurred_date,
            description=result.description,
            user_id=result.user_id,
        )
