from typing import Annotated
from uuid import UUID

from application.commands import (
    CategoryData,
    CreateBudgetCommand,
    DeactivateBudgetCommand,
    RenewBudgetCommand,
)
from application.commands.handlers.command_handler import CommandHandler
from application.dtos import BudgetDTO
from application.dtos.category_list_dto import CategoryListDTO
from application.dtos.paginated_item_dto import PaginatedItemDTO
from application.queries.get_budget_by_id_query import GetBudgetByIdQuery
from application.queries.get_budgets_query import GetBudgetsQuery
from application.queries.get_categories_query import GetCategoriesQuery
from application.queries.handlers.query_handler import QueryHandler
from dependency_injector.wiring import Provide, inject
from domain.value_objects import (
    BudgetStrategyInput,
    MonthlyBudgetStrategyInput,
    YearlyBudgetStrategyInput,
)
from domain.value_objects.budget_strategy import BudgetStrategyType
from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from infrastructure.container.main_container import MainContainer

from adapters.inbound.api.payloads.payloads import (
    CreateBudgetRequestPayload,
    CreateCategoryRequestPayload,
    StrategyPayload,
)
from adapters.outbound.persistence.in_memory.database import DEFAULT_USER_ID

router = APIRouter(tags=["budgets"])


def _map_category_create_to_data(
    category: CreateCategoryRequestPayload,
) -> CategoryData:
    """Map CategoryCreate payload to CategoryData for command."""
    return CategoryData(name=category.name, limit=category.limit.amount)


def _map_strategy_to_input(
    strategy_payload: StrategyPayload,
) -> BudgetStrategyInput:
    """Map strategy payload to domain BudgetStrategyInput."""
    match strategy_payload.budget_strategy_type:
        case BudgetStrategyType.MONTHLY:
            return MonthlyBudgetStrategyInput(
                start_day=strategy_payload.parameters.get("start_day", 1)
            )  # Default start day
        case BudgetStrategyType.YEARLY:
            return YearlyBudgetStrategyInput()
        case _:
            raise ValueError(
                f"Unsupported strategy type: {strategy_payload.budget_strategy_type}"
            )


@router.get("/")
@inject
async def get_budgets(
    query_handler: Annotated[
        QueryHandler[GetBudgetsQuery, PaginatedItemDTO[BudgetDTO]],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_query_handler.call(
                    GetBudgetsQuery
                )
            ]
        ),
    ],
    status: str | None = Query(None, description="Filter by 'active' or 'expired'"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort: str | None = Query(None, description="Field to sort by"),
) -> PaginatedItemDTO[BudgetDTO]:
    """
    Retrieve a list of budgets with pagination and filtering options.

    Args:
        status: Optional filter for budget status ('active' or 'expired')
        page: Page number for pagination
        limit: Number of items per page
        sort: Field to sort results by
        query_handler: Injected query handler for retrieving budgets
    """
    user_id = DEFAULT_USER_ID
    query = GetBudgetsQuery(
        status=status,
        page=page,
        limit=limit,
        sort=sort,
        user_id=user_id,
    )
    return await query_handler.handle(query)


@router.post("/", status_code=http_status.HTTP_201_CREATED)
@inject
async def create_budget(
    payload: CreateBudgetRequestPayload,
    command_handler: Annotated[
        CommandHandler[CreateBudgetCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    CreateBudgetCommand
                )
            ]
        ),
    ],
):
    """
    Create a new budget.

    Args:
        payload: Budget creation data.
        command_handler: Injected handler for the CreateBudgetCommand.
    """
    user_id = DEFAULT_USER_ID
    command = CreateBudgetCommand(
        user_id=user_id,
        total_limit=payload.total_limit.amount,
        currency=payload.total_limit.currency,
        strategy_input=_map_strategy_to_input(payload.strategy),
        start_date=payload.start_date,
        categories=[_map_category_create_to_data(cat) for cat in payload.categories],
        name=payload.name,
    )
    await command_handler.handle(command)


@router.get("/{budget_id}", response_model=BudgetDTO)
@inject
async def get_budget_by_id(
    budget_id: UUID,
    query_handler: Annotated[
        QueryHandler[GetBudgetByIdQuery, BudgetDTO],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_query_handler.call(
                    GetBudgetByIdQuery
                )
            ]
        ),
    ],
) -> BudgetDTO:
    """
    Retrieve detailed information for a specific budget.

    Args:
        budget_id: The UUID of the budget to retrieve.
        query_handler: Injected query handler for retrieving budget details.
    """
    user_id = DEFAULT_USER_ID
    query = GetBudgetByIdQuery(budget_id=budget_id, user_id=user_id)
    return await query_handler.handle(query)


@router.patch("/{budget_id}/deactivate", status_code=http_status.HTTP_200_OK)
@inject
async def deactivate_budget(
    budget_id: UUID,
    command_handler: Annotated[
        CommandHandler[DeactivateBudgetCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    DeactivateBudgetCommand
                )
            ]
        ),
    ],
):
    """
    Deactivate a budget to prevent automatic renewal.

    Args:
        budget_id: The UUID of the budget to deactivate.
        command_handler: Injected handler for the DeactivateBudgetCommand.
    """
    user_id = DEFAULT_USER_ID
    command = DeactivateBudgetCommand(user_id=user_id, budget_id=budget_id)
    await command_handler.handle(command)


@router.post("/{budget_id}/renew", status_code=http_status.HTTP_200_OK)
@inject
async def renew_budget(
    budget_id: UUID,
    command_handler: Annotated[
        CommandHandler[RenewBudgetCommand],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_command_handler.call(
                    RenewBudgetCommand
                )
            ]
        ),
    ],
):
    """
    Manually trigger budget renewal based on the defined strategy.

    Args:
        budget_id: The UUID of the budget to renew.
        command_handler: Injected handler for the RenewBudgetCommand.
    """
    user_id = DEFAULT_USER_ID
    command = RenewBudgetCommand(user_id=user_id, budget_id=budget_id)
    await command_handler.handle(command)


@router.get("/{budget_id}/categories")
@inject
async def get_categories(
    budget_id: UUID,
    query_handler: Annotated[
        QueryHandler[GetCategoriesQuery, CategoryListDTO],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_query_handler.call(
                    GetCategoriesQuery
                )
            ]
        ),
    ],
) -> CategoryListDTO:
    """
    Retrieve all categories associated with a specific budget.

    Args:
        budget_id: The UUID of the budget.
        query_handler: Injected query handler for retrieving categories.
    """
    user_id = DEFAULT_USER_ID
    query = GetCategoriesQuery(budget_id=budget_id, user_id=user_id)
    return await query_handler.handle(query)
