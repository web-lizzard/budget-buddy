from fastapi import APIRouter

from .budgets import router as budgets_router


def create_budget_router() -> APIRouter:
    router = APIRouter(prefix="/budgets", tags=["budgets"])

    router.include_router(budgets_router)

    return router
