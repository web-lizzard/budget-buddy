from typing import Annotated
from uuid import UUID

from application.dtos.statistics_record_dto import StatisticsRecordDTO
from application.queries.get_budget_statistics_query import GetBudgetStatisticsQuery
from application.queries.handlers.query_handler import QueryHandler
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from infrastructure.container.app_container import AppContainer

router = APIRouter(tags=["statistics"])


@router.get("/{budget_id}/statistics")
@inject
async def get_budget_statistics(
    budget_id: UUID,
    query_handler: Annotated[
        QueryHandler[GetBudgetStatisticsQuery, StatisticsRecordDTO],
        Depends(
            Provide[
                AppContainer.persistence_container.provided.get_query_handler.call(
                    GetBudgetStatisticsQuery
                )
            ]
        ),
    ],
) -> StatisticsRecordDTO:
    """
    Retrieve overall financial statistics for a budget.

    Args:
        budget_id: The UUID of the budget.
        query_handler: Injected query handler for retrieving statistics.
    """
    query = GetBudgetStatisticsQuery(budget_id=budget_id)
    return await query_handler.handle(query)
