from fastapi import FastAPI
from app.api.v1.sales import router as sales_router

app = FastAPI()

app.include_router(sales_router)