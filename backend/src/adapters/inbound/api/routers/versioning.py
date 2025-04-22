from fastapi import APIRouter

from .budgets import create_budget_router


def create_v0_router() -> APIRouter:
    """Create v0 API router.

    Returns:
        APIRouter: Configured v0 router
    """
    router = APIRouter(
        prefix="/v0",
        tags=["v0"],
    )

    router.include_router(create_budget_router())

    return router
