from typing import Annotated
from uuid import UUID

from application.dtos.statistics_record_dto import StatisticsRecordDTO
from application.queries.get_budget_statistics_query import GetBudgetStatisticsQuery
from application.queries.handlers.query_handler import QueryHandler
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from infrastructure.container.main_container import MainContainer

from backend.src.adapters.inbound.api.dependencies.auth import get_current_user_id

router = APIRouter(tags=["statistics"])


@router.get("/{budget_id}/statistics")
@inject
async def get_budget_statistics(
    budget_id: UUID,
    query_handler: Annotated[
        QueryHandler[GetBudgetStatisticsQuery, StatisticsRecordDTO],
        Depends(
            Provide[
                MainContainer.application_container.provided.get_query_handler.call(
                    GetBudgetStatisticsQuery
                )
            ]
        ),
    ],
    user_id_str: str = Depends(get_current_user_id),
) -> StatisticsRecordDTO:
    """
    Retrieve overall financial statistics for a budget.

    Args:
        budget_id: The UUID of the budget.
        query_handler: Injected query handler for retrieving statistics.
    """
    user_id = UUID(user_id_str)
    print(
        f"Handling get_budget_statistics for user_id: {user_id}, budget_id: {budget_id}"
    )
    query = GetBudgetStatisticsQuery(budget_id=budget_id, user_id=user_id)
    return await query_handler.handle(query)
