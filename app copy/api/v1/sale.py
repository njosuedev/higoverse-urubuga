from fastapi import APIRouter
from app.modules.sales.router import router as sales_router

router = APIRouter()

router.include_router(
    sales_router,
    prefix="/sales",
    tags=["Sales"]
)