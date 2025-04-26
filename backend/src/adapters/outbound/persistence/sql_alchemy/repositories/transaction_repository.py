import uuid
from typing import Sequence

from domain.aggregates.transaction import Transaction
from domain.exceptions import TransactionNotFoundError
from domain.ports.transaction_repository import TransactionRepository
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..mappers.transaction_mapper import (
    map_transaction_domain_to_model,
    map_transaction_model_to_domain,
)
from ..models import BudgetModel, CategoryModel, TransactionModel


class SQLAlchemyTransactionRepository(TransactionRepository):
    """SQLAlchemy implementation of the TransactionRepository port."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(
        self, transaction_id: uuid.UUID, user_id: uuid.UUID
    ) -> Transaction:
        """Find transaction by ID for a specific user."""
        # Use session.get for primary key lookups if possible, it's faster
        transaction_model = await self._session.get(TransactionModel, transaction_id)

        if transaction_model is None or transaction_model.user_id != user_id:
            raise TransactionNotFoundError(str(transaction_id))

        return map_transaction_model_to_domain(transaction_model)

    async def find_by_budget_id(
        self, budget_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[Transaction]:
        """Find transactions by budget ID and user ID."""
        stmt = (
            select(TransactionModel)
            .join(TransactionModel.category)
            .join(CategoryModel.budget)
            .where(
                BudgetModel.id == budget_id,
                TransactionModel.user_id == user_id,
                BudgetModel.user_id == user_id,
            )
            .order_by(TransactionModel.occurred_date.desc())
        )
        result = await self._session.execute(stmt)
        transaction_models = result.scalars().all()
        return [map_transaction_model_to_domain(model) for model in transaction_models]

    async def find_by_category_id(
        self, category_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[Transaction]:
        stmt = (
            select(TransactionModel)
            .where(
                TransactionModel.category_id == category_id,
                TransactionModel.user_id == user_id,
            )
            .order_by(TransactionModel.occurred_date.desc())
        )
        result = await self._session.execute(stmt)
        transaction_models = result.scalars().all()
        return [map_transaction_model_to_domain(model) for model in transaction_models]

    async def save(self, transaction: Transaction) -> None:
        transaction_model = map_transaction_domain_to_model(transaction)
        await self._session.merge(transaction_model)

    async def delete(self, transaction: Transaction) -> None:
        existing_model = await self._session.get(TransactionModel, transaction.id)
        if existing_model is None or existing_model.user_id != transaction.user_id:
            raise TransactionNotFoundError(str(transaction.id))

        await self._session.delete(existing_model)

    async def save_bulk(self, transactions: list[Transaction]) -> None:
        if not transactions:
            raise TransactionNotFoundError(
                "Transactions not found to save",
            )
        transaction_models = [map_transaction_domain_to_model(t) for t in transactions]
        for model in transaction_models:
            await self._session.merge(model)

    async def delete_bulk(self, transactions: list[Transaction]) -> None:
        if not transactions:
            raise TransactionNotFoundError(
                "Transactions not found to delete",
            )

        transaction_ids = [t.id for t in transactions]
        user_id = transactions[0].user_id

        verification_stmt = select(TransactionModel.id).where(
            TransactionModel.id.in_(transaction_ids),
            TransactionModel.user_id == user_id,
        )
        result = await self._session.execute(verification_stmt)
        verified_ids_to_delete: Sequence[uuid.UUID] = result.scalars().all()

        if not verified_ids_to_delete:
            raise TransactionNotFoundError(
                "Transactions not found to delete",
            )

        stmt = delete(TransactionModel).where(
            TransactionModel.id.in_(verified_ids_to_delete)
        )
        await self._session.execute(stmt)
