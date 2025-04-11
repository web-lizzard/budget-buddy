import uvicorn
from fastapi import FastAPI

from adapters.driving.api.routers import monitoring
from configuration import Environment, get_configuration


def create_app() -> FastAPI:
    configuration = get_configuration()
    app = FastAPI(
        title="Budget Buddy API",
        description="API for Budget Buddy application",
        version=configuration.api.version,
    )

    # Register routers
    app.include_router(monitoring.router)

    return app


def run_webservice() -> None:
    configuration = get_configuration()
    reload = configuration.environment == Environment.DEVELOPMENT
    uvicorn.run(
        f"{__name__}:{create_app.__name__}",
        host="0.0.0.0",
        port=configuration.api.port,
        reload=reload,
        reload_dirs=["src"],
        factory=True,
    )
