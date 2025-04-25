import uuid

from application.dtos import TransactionDTO
from application.queries import GetTransactionByIdQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import TransactionNotFoundError

# Assuming domain Transaction exists and IN_MEMORY_DATABASE structure
from adapters.outbound.persistence.in_memory.database import (
    DEFAULT_USER_ID,  # Using default user ID for this handler
    IN_MEMORY_DATABASE,
)

from .mappers import map_transaction_to_dto


class GetTransactionByIdQueryHandler(
    QueryHandler[GetTransactionByIdQuery, TransactionDTO]
):
    """Handles the GetTransactionByIdQuery for the in-memory repository.
    NOTE: Uses DEFAULT_USER_ID as user_id is not part of the query.
          Assumes transaction_id is a UUID convertible string.
          Does not validate budget_id against the found transaction.
    """

    async def handle(self, query: GetTransactionByIdQuery) -> TransactionDTO:
        """Retrieves a specific transaction by its ID for the default user.

        Args:
            query: The GetTransactionByIdQuery containing transaction_id (as string).

        Returns:
            The corresponding TransactionDTO.

        Raises:
            TransactionNotFoundError: If the transaction is not found or doesn't belong to the default user.
        """
        user_id_to_check = DEFAULT_USER_ID

        transaction_uuid = uuid.UUID(query.transaction_id)

        transactions_table = IN_MEMORY_DATABASE.get_database().get("transactions", {})
        transaction = transactions_table.get(transaction_uuid)

        if not transaction or transaction.user_id != user_id_to_check:
            raise TransactionNotFoundError(
                f"Transaction with ID {query.transaction_id} not found."
            )

        transaction_dto = map_transaction_to_dto(transaction)
        return transaction_dto
