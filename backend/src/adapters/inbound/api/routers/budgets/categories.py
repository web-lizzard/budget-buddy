from typing import Annotated
from uuid import UUID

from application.commands.add_category_command import AddCategoryCommand
from application.commands.edit_category_command import EditCategoryCommand
from application.commands.handlers.command_handler import CommandHandler
from application.commands.remove_category_command import RemoveCategoryCommand
from application.dtos.category_dto import CategoryDTO
from application.queries.get_category_by_id_query import GetCategoryByIdQuery
from application.queries.handlers.query_handler import QueryHandler
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi import status as http_status
from infrastructure.container.main_container import MainContainer

# Import the dependency for getting current user ID
from adapters.inbound.api.dependencies.auth import get_current_user_id
from adapters.inbound.api.payloads.payloads import (
    CreateCategoryRequestPayload,
    DeleteCategoryRequestPayload,
    UpdateCategoryRequestPayload,
)

# from adapters.outbound.persistence.in_memory.database import DEFAULT_USER_ID # Removed

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
                MainContainer.application_container.provided.get_query_handler.call(
                    GetCategoryByIdQuery
                )
            ]
        ),
    ],
    user_id_str: str = Depends(get_current_user_id),  # Added user_id dependency
) -> CategoryDTO:
    """
    Retrieve details for a specific category in a budget.

    Args:
        budget_id: The UUID of the budget.
        category_id: The UUID of the category to retrieve.
        query_handler: Injected query handler for retrieving category details.
    """
    user_id = UUID(user_id_str)  # Convert to UUID
    print(
        f"Handling get_category_by_id for user_id: {user_id}, budget_id: {budget_id}, category_id: {category_id}"
    )
    query = GetCategoryByIdQuery(
        budget_id=budget_id, category_id=category_id, user_id=user_id
    )
    return await query_handler.handle(query)


@router.post("/{budget_id}/categories", status_code=http_status.HTTP_201_CREATED)
@inject
async def create_category(
    budget_id: UUID,
    payload: CreateCategoryRequestPayload,
    command_handler: Annotated[
        CommandHandler[AddCategoryCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    AddCategoryCommand
                )
            ]
        ),
    ],
    user_id_str: str = Depends(get_current_user_id),  # Added user_id dependency
):
    """
    Create a new category within a given budget.

    Args:
        budget_id: The UUID of the budget to add the category to.
        payload: Category creation data.
        command_handler: Injected handler for AddCategoryCommand.
    """
    user_id = UUID(user_id_str)  # Convert to UUID
    print(f"Handling create_category for user_id: {user_id}, budget_id: {budget_id}")
    command = AddCategoryCommand(
        user_id=user_id,  # Changed to UUID
        budget_id=budget_id,  # Changed to UUID
        name=payload.name,
        limit=payload.limit.amount,
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
    command_handler: Annotated[
        CommandHandler[EditCategoryCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    EditCategoryCommand
                )
            ]
        ),
    ],
    user_id_str: str = Depends(get_current_user_id),  # Added user_id dependency
):
    """
    Update an existing category's details.

    Args:
        budget_id: The UUID of the budget containing the category.
        category_id: The UUID of the category to update.
        payload: Updated category data.
        command_handler: Injected handler for EditCategoryCommand.
    """
    user_id = UUID(user_id_str)  # Convert to UUID
    print(
        f"Handling update_category for user_id: {user_id}, budget_id: {budget_id}, category_id: {category_id}"
    )
    command = EditCategoryCommand(
        user_id=user_id,  # Changed to UUID
        budget_id=budget_id,  # Changed to UUID
        category_id=category_id,  # Changed to UUID
        name=payload.name,
        limit=payload.limit.amount,
        # Currency is handled by the domain based on budget
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
    command_handler: Annotated[
        CommandHandler[RemoveCategoryCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    RemoveCategoryCommand
                )
            ]
        ),
    ],
    user_id_str: str = Depends(get_current_user_id),  # Added user_id dependency
):
    """
    Delete a category from a budget.

    Handles associated transactions based on the provided transfer policy in the payload.

    Args:
        budget_id: The UUID of the budget containing the category.
        category_id: The UUID of the category to delete.
        payload: Payload specifying the transfer policy for transactions.
        command_handler: Injected handler for RemoveCategoryCommand.
    """
    user_id = UUID(user_id_str)  # Convert to UUID
    print(
        f"Handling delete_category for user_id: {user_id}, budget_id: {budget_id}, category_id: {category_id}"
    )

    target_category_id_uuid = None
    if (
        payload.handle_transaction.type == "move"
        and payload.handle_transaction.target_category_id
    ):
        target_category_id_uuid = UUID(
            str(payload.handle_transaction.target_category_id)
        )  # Ensure UUID

    command = RemoveCategoryCommand(
        user_id=user_id,  # Changed to UUID
        budget_id=budget_id,  # Changed to UUID
        category_id=category_id,  # Changed to UUID
        handle_transactions=payload.handle_transaction.type,
        target_category_id=target_category_id_uuid,  # Changed to UUID or None
    )
    await command_handler.handle(command)
