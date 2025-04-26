from typing import Annotated
from uuid import UUID

from application.commands.add_category_command import AddCategoryCommand
from application.commands.edit_category_command import EditCategoryCommand
from application.commands.handlers.add_category_command_handler import (
    AddCategoryCommandHandler,
)
from application.commands.handlers.edit_category_command_handler import (
    EditCategoryCommandHandler,
)
from application.commands.handlers.remove_category_command_handler import (
    RemoveCategoryCommandHandler,
)
from application.commands.remove_category_command import RemoveCategoryCommand
from application.dtos.category_dto import CategoryDTO
from application.ports.uow.uow import UnitOfWork
from application.queries.get_category_by_id_query import GetCategoryByIdQuery
from application.queries.handlers.query_handler import QueryHandler
from dependency_injector.wiring import Provide, inject
from domain.ports.budget_repository import BudgetRepository
from domain.ports.transaction_repository import TransactionRepository
from fastapi import APIRouter, Depends
from fastapi import status as http_status
from infrastracture.container.app_container import AppContainer

from adapters.inbound.api.payloads.payloads import (
    CreateCategoryRequestPayload,
    DeleteCategoryRequestPayload,
    UpdateCategoryRequestPayload,
)
from adapters.outbound.persistence.in_memory.database import DEFAULT_USER_ID

router = APIRouter(tags=["categories"])


@router.get("/{budget_id}/categories/{category_id}")
@inject
async def get_category_by_id(
    budget_id: UUID,
    category_id: UUID,
    query_handler: Annotated[
        QueryHandler[GetCategoryByIdQuery, CategoryDTO],
        Depends(
            Provide[
                AppContainer.persistence_container.provided.get_query_handler.call(
                    GetCategoryByIdQuery
                )
            ]
        ),
    ],
) -> CategoryDTO:
    """
    Retrieve details for a specific category in a budget.

    Args:
        budget_id: The UUID of the budget.
        category_id: The UUID of the category to retrieve.
        query_handler: Injected query handler for retrieving category details.
    """
    query = GetCategoryByIdQuery(budget_id=budget_id, category_id=category_id)
    return await query_handler.handle(query)


@router.post("/{budget_id}/categories", status_code=http_status.HTTP_201_CREATED)
@inject
async def create_category(
    budget_id: UUID,
    payload: CreateCategoryRequestPayload,
    budget_repository: Annotated[
        BudgetRepository,
        Depends(
            Provide[
                AppContainer.persistence_container.provided.get_repository.call(
                    BudgetRepository
                )
            ]
        ),
    ],
    unit_of_work: Annotated[
        UnitOfWork, Depends(Provide[AppContainer.persistence_container.uow])
    ],
):
    """
    Create a new category within a given budget.

    Args:
        budget_id: The UUID of the budget to add the category to.
        payload: Category creation data.
        budget_repository: Repository for budget persistence.
        unit_of_work: Unit of work for transaction management.
    """
    # TODO: Replace with actual authenticated user ID later
    user_id = DEFAULT_USER_ID
    command = AddCategoryCommand(
        user_id=str(user_id),
        budget_id=str(budget_id),
        name=payload.name,
        limit=payload.limit.amount,
    )
    command_handler = AddCategoryCommandHandler(
        budget_repository=budget_repository,
        unit_of_work=unit_of_work,
    )
    await command_handler.handle(command)


@router.put(
    "/{budget_id}/categories/{category_id}", status_code=http_status.HTTP_200_OK
)
@inject
async def update_category(
    budget_id: UUID,
    category_id: UUID,
    payload: UpdateCategoryRequestPayload,
    budget_repository: Annotated[
        BudgetRepository,
        Depends(
            Provide[
                AppContainer.persistence_container.provided.get_repository.call(
                    BudgetRepository
                )
            ]
        ),
    ],
    unit_of_work: Annotated[
        UnitOfWork, Depends(Provide[AppContainer.persistence_container.uow])
    ],
):
    """
    Update an existing category's details.

    Args:
        budget_id: The UUID of the budget containing the category.
        category_id: The UUID of the category to update.
        payload: Updated category data.
        budget_repository: Repository for budget persistence.
        unit_of_work: Unit of work for transaction management.
    """
    # TODO: Replace with actual authenticated user ID later
    user_id = DEFAULT_USER_ID
    command = EditCategoryCommand(
        user_id=str(user_id),
        budget_id=str(budget_id),
        category_id=str(category_id),
        name=payload.name,
        limit=payload.limit.amount,
        # Currency is handled by the domain based on budget
    )
    command_handler = EditCategoryCommandHandler(
        budget_repository=budget_repository, unit_of_work=unit_of_work
    )
    await command_handler.handle(command)


@router.delete(
    "/{budget_id}/categories/{category_id}", status_code=http_status.HTTP_200_OK
)
@inject
async def delete_category(
    budget_id: UUID,
    category_id: UUID,
    # Using payload instead of query param based on payloads.py and handler structure
    payload: DeleteCategoryRequestPayload,
    budget_repository: Annotated[
        BudgetRepository,
        Depends(
            Provide[
                AppContainer.persistence_container.provided.get_repository.call(
                    BudgetRepository
                )
            ]
        ),
    ],
    transaction_repository: Annotated[
        TransactionRepository,
        Depends(
            Provide[
                AppContainer.persistence_container.provided.get_repository.call(
                    TransactionRepository
                )
            ]
        ),
    ],
    unit_of_work: Annotated[
        UnitOfWork, Depends(Provide[AppContainer.persistence_container.uow])
    ],
):
    """
    Delete a category from a budget.

    Handles associated transactions based on the provided transfer policy in the payload.

    Args:
        budget_id: The UUID of the budget containing the category.
        category_id: The UUID of the category to delete.
        payload: Payload specifying the transfer policy for transactions.
        budget_repository: Repository for budget persistence.
        transaction_repository: Repository for transaction operations.
        unit_of_work: Unit of work for transaction management.
    """
    # TODO: Replace with actual authenticated user ID later
    # User ID from payload might be redundant if we use authenticated user context
    user_id = DEFAULT_USER_ID  # Or use authenticated user ID

    target_category_id_str = None
    if payload.handle_transaction.type == "move":
        # Make sure target_category_id is converted to string if handler expects it
        target_category_id_str = str(payload.handle_transaction.target_category_id)

    command = RemoveCategoryCommand(
        user_id=str(user_id),
        budget_id=str(budget_id),
        category_id=str(category_id),
        handle_transactions=payload.handle_transaction.type,
        target_category_id=target_category_id_str,
    )
    command_handler = RemoveCategoryCommandHandler(
        unit_of_work=unit_of_work,
        budget_repository=budget_repository,
        transaction_repository=transaction_repository,
    )
    await command_handler.handle(command)
