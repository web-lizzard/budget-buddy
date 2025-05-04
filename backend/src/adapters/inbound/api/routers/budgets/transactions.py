from typing import Annotated
from uuid import UUID

from application.commands.create_transaction_command import CreateTransactionCommand
from application.commands.delete_transaction_command import DeleteTransactionCommand
from application.commands.edit_transaction_command import EditTransactionCommand
from application.commands.handlers.command_handler import CommandHandler
from application.dtos.paginated_item_dto import PaginatedItemDTO
from application.dtos.transaction_dto import TransactionDTO
from application.queries.get_transaction_by_id_query import GetTransactionByIdQuery
from application.queries.get_transactions_query import GetTransactionsQuery
from application.queries.handlers.query_handler import QueryHandler
from dependency_injector.wiring import Provide, inject
from domain.value_objects.money import Money
from domain.value_objects.transaction_type import TransactionType
from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from infrastructure.container.main_container import MainContainer

from adapters.inbound.api.payloads.payloads import (
    CreateTransactionRequestPayload,
    UpdateTransactionRequestPayload,
)
from adapters.outbound.persistence.in_memory.database import DEFAULT_USER_ID

router = APIRouter(tags=["transactions"])


@router.get(
    "/{budget_id}/transactions", response_model=PaginatedItemDTO[TransactionDTO]
)
@inject
async def get_transactions(
    budget_id: UUID,
    query_handler: Annotated[
        QueryHandler[GetTransactionsQuery, PaginatedItemDTO[TransactionDTO]],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_query_handler.call(
                    GetTransactionsQuery
                )
            ]
        ),
    ],
    date_from: str | None = Query(
        None, description="Filter transactions from this date (YYYY-MM-DD)"
    ),
    date_to: str | None = Query(
        None, description="Filter transactions up to this date (YYYY-MM-DD)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort: str | None = Query(
        None, description="Field to sort by (e.g., 'occurred_date')"
    ),
) -> PaginatedItemDTO[TransactionDTO]:
    """
    Retrieve a list of transactions for a specified budget.

    Args:
        budget_id: The UUID of the budget.
        query_handler: Injected query handler for retrieving transactions.
        date_from: Optional start date filter.
        date_to: Optional end date filter.
        page: Page number for pagination.
        limit: Number of items per page.
        sort: Field to sort results by.
    """
    # TODO: Replace with actual authenticated user ID later
    user_id = DEFAULT_USER_ID
    query = GetTransactionsQuery(
        budget_id=budget_id,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit,
        sort=sort,
    )
    return await query_handler.handle(query)


@router.get("/{budget_id}/transactions/{transaction_id}", response_model=TransactionDTO)
@inject
async def get_transaction_by_id(
    budget_id: UUID,
    transaction_id: UUID,
    query_handler: Annotated[
        QueryHandler[GetTransactionByIdQuery, TransactionDTO],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_query_handler.call(
                    GetTransactionByIdQuery
                )
            ]
        ),
    ],
) -> TransactionDTO:
    """
    Retrieve details for a specific transaction.

    Args:
        budget_id: The UUID of the budget.
        transaction_id: The UUID of the transaction to retrieve.
        query_handler: Injected query handler for retrieving transaction details.
    """
    user_id = DEFAULT_USER_ID
    query = GetTransactionByIdQuery(
        budget_id=budget_id, transaction_id=str(transaction_id), user_id=user_id
    )
    return await query_handler.handle(query)


@router.post("/{budget_id}/transactions", status_code=http_status.HTTP_201_CREATED)
@inject
async def create_transaction(
    budget_id: UUID,
    payload: CreateTransactionRequestPayload,
    command_handler: Annotated[
        CommandHandler[CreateTransactionCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    CreateTransactionCommand
                )
            ]
        ),
    ],
):
    """
    Create a new transaction in a budget category.

    Args:
        budget_id: The UUID of the budget.
        payload: Transaction creation data.
        command_handler: Injected handler for CreateTransactionCommand.
    """
    # TODO: Replace with actual authenticated user ID later
    # user_id should come from payload or auth context
    user_id = DEFAULT_USER_ID

    # Map payload enum string value to domain TransactionType enum
    domain_transaction_type = TransactionType[payload.transaction_type.value]

    command = CreateTransactionCommand(
        category_id=payload.category_id,
        amount=payload.amount.amount,
        transaction_type=domain_transaction_type,  # Use domain enum
        budget_id=budget_id,
        user_id=user_id,
        occurred_date=payload.occurred_date,
        description=payload.description,
    )
    await command_handler.handle(command)


@router.put(
    "/{budget_id}/transactions/{transaction_id}", status_code=http_status.HTTP_200_OK
)
@inject
async def update_transaction(
    budget_id: UUID,
    transaction_id: UUID,
    payload: UpdateTransactionRequestPayload,
    command_handler: Annotated[
        CommandHandler[EditTransactionCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    EditTransactionCommand
                )
            ]
        ),
    ],
):
    """
    Update an existing transaction.

    Args:
        budget_id: The UUID of the budget containing the transaction.
        transaction_id: The UUID of the transaction to update.
        payload: Updated transaction data.
        command_handler: Injected handler for EditTransactionCommand.
    """
    user_id = DEFAULT_USER_ID

    domain_transaction_type = TransactionType[payload.transaction_type.value]

    money_amount = Money.mint(payload.amount.amount, payload.amount.currency)

    command = EditTransactionCommand(
        transaction_id=transaction_id,
        budget_id=budget_id,
        user_id=user_id,
        category_id=payload.category_id,
        amount=money_amount,
        transaction_type=domain_transaction_type,
        description=payload.description,
    )
    await command_handler.handle(command)


@router.delete(
    "/{budget_id}/transactions/{transaction_id}", status_code=http_status.HTTP_200_OK
)
@inject
async def delete_transaction(
    budget_id: UUID,
    transaction_id: UUID,
    command_handler: Annotated[
        CommandHandler[DeleteTransactionCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    DeleteTransactionCommand
                )
            ]
        ),
    ],
):
    """
    Delete a transaction.

    Args:
        budget_id: The UUID of the budget containing the transaction.
        transaction_id: The UUID of the transaction to delete.
        command_handler: Injected handler for DeleteTransactionCommand.
    """
    user_id = DEFAULT_USER_ID

    command = DeleteTransactionCommand(
        transaction_id=transaction_id,
        budget_id=budget_id,
        user_id=user_id,
    )

    await command_handler.handle(command)
