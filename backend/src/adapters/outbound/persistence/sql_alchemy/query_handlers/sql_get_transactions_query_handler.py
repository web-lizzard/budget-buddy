from datetime import datetime

from application.dtos import (
    MoneyDTO,
    PaginatedItemDTO,
    TransactionDTO,
    TransactionTypeEnum,
)
from application.queries import GetTransactionsQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import BudgetNotFoundError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import BudgetModel, TransactionModel


class SQLGetTransactionsQueryHandler(
    QueryHandler[GetTransactionsQuery, PaginatedItemDTO[TransactionDTO]]
):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def handle(
        self, query: GetTransactionsQuery
    ) -> PaginatedItemDTO[TransactionDTO]:
        skip = (query.page - 1) * query.limit

        budget_check_stmt = select(BudgetModel.id).where(
            BudgetModel.id == query.budget_id, BudgetModel.user_id == query.user_id
        )
        budget_exists = await self._session.scalar(budget_check_stmt)

        if not budget_exists:
            raise BudgetNotFoundError(
                f"Budget with id {query.budget_id} not found for user {query.user_id}."
            )

        base_where = (TransactionModel.user_id == query.user_id,)

        stmt = select(TransactionModel).where(*base_where)
        count_stmt = select(func.count(TransactionModel.id)).where(*base_where)

        if query.date_from:
            date_from = datetime.fromisoformat(query.date_from)
            stmt = stmt.where(TransactionModel.occurred_date >= date_from)
            count_stmt = count_stmt.where(TransactionModel.occurred_date >= date_from)
        if query.date_to:
            date_to = datetime.fromisoformat(query.date_to)
            stmt = stmt.where(TransactionModel.occurred_date <= date_to)
            count_stmt = count_stmt.where(TransactionModel.occurred_date <= date_to)

        if query.sort:
            sort_field = query.sort.lstrip("-")
            sort_column = getattr(TransactionModel, sort_field, None)
            if sort_column:
                if query.sort.startswith("-"):
                    stmt = stmt.order_by(sort_column.desc())
                else:
                    stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(TransactionModel.occurred_date.desc())

        stmt = stmt.offset(skip).limit(query.limit)

        result = await self._session.scalars(stmt)
        total_count = await self._session.scalar(count_stmt) or 0

        transaction_dtos = [
            TransactionDTO(
                id=tx.id,
                category_id=tx.category_id,
                amount=MoneyDTO(amount=tx.amount.amount, currency=tx.amount.currency),
                transaction_type=TransactionTypeEnum(tx.transaction_type.value),
                occurred_date=tx.occurred_date,
                description=tx.description,
                user_id=tx.user_id,
            )
            for tx in result.all()
        ]

        return PaginatedItemDTO(
            items=transaction_dtos, total=total_count, skip=skip, limit=query.limit
        )
