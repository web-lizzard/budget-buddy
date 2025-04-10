import uvicorn
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    return app


def run_webservice() -> None:
    uvicorn.run(
        create_app(),
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
    )
