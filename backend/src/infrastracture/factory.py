from fastapi import FastAPI

from .application import ContainerizedFastAPI
from .container import Container
from .logging import configure_logging
from .settings import get_settings


def create_app() -> FastAPI:
    """Create and configure the application.

    Returns:
        FastAPI: Configured application instance
    """
    # Initialize settings
    settings = get_settings()

    # Configure logging
    configure_logging(settings)

    # Create and configure the container
    container = Container()
    container.wire(
        packages=[
            "adapters.inbound.http.routes",
            "application.services",
        ]
    )

    # Create the application
    app = ContainerizedFastAPI(
        container=container,
        title="Budget Buddy API",
        description="API for managing personal budgets",
        version="1.0.0",
    )

    return app
