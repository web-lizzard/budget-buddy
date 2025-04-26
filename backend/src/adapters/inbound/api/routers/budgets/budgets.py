from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from application.commands import (
    CategoryData,
    CreateBudgetCommand,
    DeactivateBudgetCommand,
    RenewBudgetCommand,
)
from application.commands.handlers.create_budget_command_handler import (
    CreateBudgetCommandHandler,
)
from application.commands.handlers.deactivate_budget_command_handler import (
    DeactivateBudgetCommandHandler,
)
from application.commands.handlers.renew_budget_command_handler import (
    RenewBudgetCommandHandler,
)
from application.dtos import BudgetDTO
from application.dtos.paginated_item_dto import PaginatedItemDTO
from application.ports.uow.uow import UnitOfWork
from application.queries.get_budget_by_id_query import GetBudgetByIdQuery
from application.queries.get_budgets_query import GetBudgetsQuery
from application.queries.handlers.query_handler import QueryHandler
from dependency_injector.wiring import Provide, inject
from domain.factories.budget_factory import BudgetFactory
from domain.ports.budget_repository import BudgetRepository
from domain.strategies.budget_strategy.budget_strategy import BudgetStrategy
from domain.value_objects import (
    BudgetStrategyInput,
    MonthlyBudgetStrategyInput,
    YearlyBudgetStrategyInput,
)
from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from infrastracture.container.app_container import AppContainer

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
    # TODO: Handle strategy parameters properly based on type
    if strategy_payload.type == "monthly":
        return MonthlyBudgetStrategyInput(
            start_day=strategy_payload.parameters.get(
                "start_day", 1
            )  # Default start day
        )
    elif strategy_payload.type == "yearly":
        return YearlyBudgetStrategyInput()
    else:
        # Handle unknown strategy type, maybe raise an error or default
        raise ValueError(f"Unknown budget strategy type: {strategy_payload.type}")


@router.get("/")
@inject
async def get_budgets(
    query_handler: Annotated[
        QueryHandler[GetBudgetsQuery, PaginatedItemDTO[BudgetDTO]],
        Depends(
            Provide[
                AppContainer.persistence_container.provided.get_query_handler.call(
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
    query = GetBudgetsQuery(
        status=status,
        page=page,
        limit=limit,
        sort=sort,
    )
    print(query_handler)
    return await query_handler.handle(query)


@router.post("/", status_code=http_status.HTTP_201_CREATED)
@inject
async def create_budget(
    payload: CreateBudgetRequestPayload,
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
    budget_factory: Annotated[
        BudgetFactory,
        Depends(Provide[AppContainer.domain_container.budget_factory]),
    ],
    unit_of_work: Annotated[
        UnitOfWork, Depends(Provide[AppContainer.persistence_container.uow])
    ],
):
    """
    Create a new budget.

    Args:
        payload: Budget creation data.
        budget_repository: Repository for budget persistence.
        budget_factory: Factory for creating budget entities.
        unit_of_work: Unit of work for transaction management.
    """
    # TODO: Replace with actual authenticated user ID
    user_id = uuid4()

    command = CreateBudgetCommand(
        user_id=user_id,
        total_limit=payload.total_limit.amount,
        currency=payload.total_limit.currency,
        strategy_input=_map_strategy_to_input(payload.strategy),
        start_date=datetime.combine(payload.start_date, datetime.min.time()),
        categories=[_map_category_create_to_data(cat) for cat in payload.categories],
        name=payload.name,
    )
    command_handler = CreateBudgetCommandHandler(
        budget_repository=budget_repository,
        budget_factory=budget_factory,
        unit_of_work=unit_of_work,
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
                AppContainer.persistence_container.provided.get_query_handler.call(
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
    query = GetBudgetByIdQuery(budget_id=budget_id)
    return await query_handler.handle(query)


@router.patch("/{budget_id}/deactivate", status_code=http_status.HTTP_200_OK)
@inject
async def deactivate_budget(
    budget_id: UUID,
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
        UnitOfWork, Depends(Provide[AppContainer.persistence_container.provided.uow])
    ],
):
    """
    Deactivate a budget to prevent automatic renewal.

    Args:
        budget_id: The UUID of the budget to deactivate.
        budget_repository: Repository for budget persistence.
        unit_of_work: Unit of work for transaction management.
    """
    user_id = DEFAULT_USER_ID
    command = DeactivateBudgetCommand(user_id=user_id, budget_id=budget_id)
    command_handler = DeactivateBudgetCommandHandler(
        budget_repository=budget_repository,
        unit_of_work=unit_of_work,
    )
    await command_handler.handle(command)


@router.post("/{budget_id}/renew", status_code=http_status.HTTP_200_OK)
@inject
async def renew_budget(
    budget_id: UUID,
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
    strategies: Annotated[
        list[BudgetStrategy], Depends(Provide[AppContainer.domain_container.strategies])
    ],
):
    """
    Manually trigger budget renewal based on the defined strategy.

    Args:
        budget_id: The UUID of the budget to renew.
        budget_repository: Repository for budget persistence.
        unit_of_work: Unit of work for transaction management.
    """
    user_id = DEFAULT_USER_ID
    command = RenewBudgetCommand(user_id=user_id, budget_id=budget_id)
    command_handler = RenewBudgetCommandHandler(
        budget_repository=budget_repository,
        unit_of_work=unit_of_work,
        strategies=strategies,
    )
    await command_handler.handle(command)
