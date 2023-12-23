from fastapi import FastAPI
from common.db.session import metadata, engine
from common.db.registry import start_mappers
from budget.web_server import router as budget_router


metadata.create_all(bind=engine)
start_mappers()

app = FastAPI()

app.include_router(budget_router)
