from fastapi import APIRouter

from .auth.router import router as auth_router
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
    router.include_router(auth_router)

    return router
