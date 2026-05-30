import pandas as pd
import os

from fastapi import UploadFile

from app.modules.sales.schema import SaleCreate
from app.modules.sales.repository import (
    create_sale_repository,
    get_sales_repository
)

from app.modules.sales.validator import (
    normalize_columns,
    required_columns
)



def create_sale_service(sale: SaleCreate):

    data = sale.model_dump()

    create_sale_repository(data)

    return {
        "success": True,
        "message": "Sale created successfully",
        "sale": data
    }



def get_sales_service():

    sales = get_sales_repository()

    return {
        "success": True,
        "total_sales": len(sales),
        "sales": sales
    }



def upload_sales_service(file: UploadFile):

    if not file.filename.endswith((".xlsx", ".xls")):
        return {
            "success": False,
            "message": "Only Excel files allowed"
        }

    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    df = pd.read_excel(file_path, dtype=str)

    df = normalize_columns(df)

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        return {
            "success": False,
            "missing_columns": missing
        }

    records = df.to_dict(orient="records")

    added = []

    for row in records:

        sale = SaleCreate(
            product_name=row.get("Product Name"),
            sale_price=float(row.get("Sale Price") or 0),
            sale_quantity=int(row.get("Sale Quantity") or 0),
            customer_name=row.get("Customer Name"),
            customer_phone=row.get("Customer Phone"),
            customer_tin=row.get("Customer TIN")
        )

        final = sale.model_dump()

        create_sale_repository(final)

        added.append(final)

    return {
        "success": True,
        "message": "Sales uploaded successfully",
        "added_sales": len(added),
        "sales": added
    }