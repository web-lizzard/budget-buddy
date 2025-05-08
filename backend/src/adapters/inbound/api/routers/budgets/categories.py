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

from adapters.inbound.api.dependencies.auth import get_current_user_id
from adapters.inbound.api.payloads.payloads import (
    CreateCategoryRequestPayload,
    DeleteCategoryRequestPayload,
    UpdateCategoryRequestPayload,
)

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
    user_id: UUID = Depends(get_current_user_id),
) -> CategoryDTO:
    """
    Retrieve details for a specific category in a budget.

    Args:
        budget_id: The UUID of the budget.
        category_id: The UUID of the category to retrieve.
        query_handler: Injected query handler for retrieving category details.
    """
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
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Create a new category within a given budget.

    Args:
        budget_id: The UUID of the budget to add the category to.
        payload: Category creation data.
        command_handler: Injected handler for AddCategoryCommand.
    """
    command = AddCategoryCommand(
        user_id=user_id,
        budget_id=budget_id,
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
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Update an existing category's details.

    Args:
        budget_id: The UUID of the budget containing the category.
        category_id: The UUID of the category to update.
        payload: Updated category data.
        command_handler: Injected handler for EditCategoryCommand.
    """
    command = EditCategoryCommand(
        user_id=user_id,
        budget_id=budget_id,
        category_id=category_id,
        name=payload.name,
        limit=payload.limit.amount,
    )
    await command_handler.handle(command)


@router.post(
    "/{budget_id}/categories/{category_id}/delete", status_code=http_status.HTTP_200_OK
)
@inject
async def delete_category(
    budget_id: UUID,
    category_id: UUID,
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
    user_id: UUID = Depends(get_current_user_id),
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

    target_category_id_uuid = None
    if (
        payload.handle_transaction.type == "move"
        and payload.handle_transaction.target_category_id
    ):
        target_category_id_uuid = UUID(
            str(payload.handle_transaction.target_category_id)
        )

    command = RemoveCategoryCommand(
        user_id=user_id,
        budget_id=budget_id,
        category_id=category_id,
        handle_transactions=payload.handle_transaction.type,
        target_category_id=target_category_id_uuid,
    )
    await command_handler.handle(command)
