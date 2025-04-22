from fastapi import APIRouter


def create_v0_router() -> APIRouter:
    """Create v0 API router.

    Returns:
        APIRouter: Configured v0 router
    """
    router = APIRouter(
        prefix="/v0",
        tags=["v0"],
    )

    return router
