from adapters.inbound.api.middlewares import ExceptionHandlerMiddleware
from adapters.inbound.api.routers import create_monitoring_router, create_v0_router
from fastapi import FastAPI

from .application import ContainerizedFastAPI
from .container import MainContainer
from .logging import configure_logging
from .settings import get_settings


def create_app() -> FastAPI:
    """Create and configure the application.

    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    configure_logging(settings)

    container = MainContainer()
    container.config.from_pydantic(settings)

    app = ContainerizedFastAPI(
        container=container,
        title="Budget Buddy API",
        description="API for managing personal budgets",
        version="1.0.0",
        redirect_slashes=False,
    )

    # Include routers
    app.include_router(create_monitoring_router())
    app.include_router(create_v0_router())

    app.add_middleware(ExceptionHandlerMiddleware)

    return app
