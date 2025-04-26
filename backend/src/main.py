import uvicorn
from infrastructure.create_app import create_app
from infrastructure.settings import get_settings

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.environment == "dev",
    )
