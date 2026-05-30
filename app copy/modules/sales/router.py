from fastapi import APIRouter, UploadFile, File
from app.modules.sales.schema import SaleCreate
from app.modules.sales.service import (
    create_sale_service,
    get_sales_service,
    upload_sales_service
)

router = APIRouter()


@router.post("/")
def create_sale(sale: SaleCreate):
    return create_sale_service(sale)


@router.get("/")
def get_sales():
    return get_sales_service()


@router.post("/upload")
def upload_sales(file: UploadFile = File(...)):
    return upload_sales_service(file)