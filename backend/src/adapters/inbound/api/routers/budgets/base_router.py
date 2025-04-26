from fastapi import APIRouter

from .budgets import router as budgets_router
from .categories import router as categories_router
from .statistics import router as statistics_router
from .transactions import router as transactions_router


def create_budget_router() -> APIRouter:
    router = APIRouter(prefix="/budgets", tags=["budgets"])

    router.include_router(budgets_router)
    router.include_router(categories_router)
    router.include_router(statistics_router)
    router.include_router(transactions_router)

    return router
