from fastapi import APIRouter, Response
from infrastracture.settings import Environment, get_settings


def create_monitoring_router() -> APIRouter:
    """Create monitoring router.

    Returns:
        APIRouter: Configured monitoring router
    """
    router = APIRouter(
        prefix="/monitoring",
        tags=["Monitoring"],
        include_in_schema=get_settings().environment != Environment.PRODUCTION,
    )

    @router.get("/liveness")
    async def liveness() -> Response:
        """Check if the application is alive.

        Returns:
            Response: 200 OK if the application is alive
        """
        return Response(status_code=200)

    @router.get("/readiness")
    async def readiness() -> Response:
        """Check if the application is ready to accept requests.

        Returns:
            Response: 200 OK if the application is ready
        """
        return Response(status_code=200)

    return router
