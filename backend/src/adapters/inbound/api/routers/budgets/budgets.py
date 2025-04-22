from fastapi import APIRouter, status

router = APIRouter(tags=["budgets"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_budget():
    pass
