from datetime import datetime

# NOTE: Linter might complain about DTOs, assume they exist in dtos.py
from application.dtos import TransactionDTO
from application.dtos.paginated_item_dto import PaginatedItemDTO
from application.queries import GetTransactionsQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import BudgetNotFoundError

# Assuming domain objects exist and IN_MEMORY_DATABASE structure
from adapters.outbound.persistence.in_memory.database import (
    DEFAULT_USER_ID,  # Using default user ID for this handler
    IN_MEMORY_DATABASE,
)

from .mappers import map_transaction_to_dto


class GetTransactionsQueryHandler(
    QueryHandler[GetTransactionsQuery, PaginatedItemDTO[TransactionDTO]]
):
    """Handles the GetTransactionsQuery for the in-memory repository.
    NOTE: Uses DEFAULT_USER_ID as user_id is not part of the query.
          Performs filtering, sorting, and pagination in memory.
          Requires fetching budget categories to filter transactions.
    """

    async def handle(
        self, query: GetTransactionsQuery
    ) -> PaginatedItemDTO[TransactionDTO]:
        """Retrieves transactions for a specific budget owned by the default user, with filtering and pagination.

        Args:
            query: The GetTransactionsQuery containing budget_id and filter/pagination options.

        Returns:
            A PaginatedItemDTO containing the filtered and paginated list of TransactionDTOs.

        Raises:
            BudgetNotFoundError: If the budget is not found for the default user.
        """
        user_id_to_check = DEFAULT_USER_ID

        # 1. Fetch the budget and its category IDs for the default user
        budgets_table = IN_MEMORY_DATABASE.get_database().get("budgets", {})
        budget_data = budgets_table.get(query.budget_id)
        if not budget_data or budget_data[1].user_id != user_id_to_check:
            raise BudgetNotFoundError(
                f"Budget with ID {query.budget_id} not found for user {user_id_to_check}"
            )
        _version, budget = budget_data
        # Assuming budget domain object has 'categories' list with 'id' attribute
        budget_category_ids = {
            getattr(cat, "id", None) for cat in getattr(budget, "categories", [])
        }
        budget_category_ids.discard(None)  # Remove None if getattr failed

        transactions_table = IN_MEMORY_DATABASE.get_database().get("transactions", {})
        all_transactions = list(transactions_table.values())

        filtered_transactions = []
        for transaction in all_transactions:
            if transaction.user_id != user_id_to_check:
                continue

            if transaction.category_id not in budget_category_ids:
                continue

            occurred_date = transaction.occurred_date

            if query.date_from:
                date_from = datetime.fromisoformat(query.date_from + "T00:00:00")
                if occurred_date < date_from:
                    continue
            if query.date_to:
                date_to = datetime.fromisoformat(query.date_to + "T23:59:59.999999")
                if occurred_date > date_to:
                    continue

            filtered_transactions.append(transaction)

        if query.sort:
            sort_field = query.sort.strip("-")
            reverse_sort = query.sort.startswith("-")

            filtered_transactions.sort(
                key=lambda t: getattr(t, sort_field, 0), reverse=reverse_sort
            )

        total_count = len(filtered_transactions)
        skip = (query.page - 1) * query.limit
        start_index = skip
        end_index = start_index + query.limit
        paginated_transactions = filtered_transactions[start_index:end_index]

        # 6. Map to DTOs
        transaction_dtos: list[TransactionDTO] = [
            map_transaction_to_dto(transaction)
            for transaction in paginated_transactions
        ]

        return PaginatedItemDTO[TransactionDTO](
            items=transaction_dtos,
            total=total_count,
            skip=skip,
            limit=query.limit,
        )
