from fastapi import APIRouter, UploadFile, File
from schemas.product_schema import Product
import pandas as pd
import shutil
import os

router = APIRouter()

# =====================================================
# TEMPORARY STORAGE
# =====================================================
products_db = []

# =====================================================
# REQUIRED EXCEL COLUMNS
# =====================================================
required_columns = ["Name", "Price", "Quantity","Customer"]


# =====================================================
# ADD SINGLE PRODUCT
# =====================================================
@router.post("/products")
def create_product(product: Product):

    # =============================================
    # CHECK DUPLICATE PRODUCT
    # =============================================
    for existing_product in products_db:

        if existing_product["name"].lower() == product.name.lower():

            return {
                "success": False,
                "error": {
                    "code": "DUPLICATE_PRODUCT",
                    "message": f"{product.name} already exists"
                }
            }

    # =============================================
    # ADD PRODUCT
    # =============================================
    products_db.append(product.dict())

    return {
        "success": True,
        "message": "Product added successfully",
        "product": product
    }


# =====================================================
# GET ALL PRODUCTS
# =====================================================
@router.get("/products")
def get_products():

    return {
        "success": True,
        "total_products": len(products_db),
        "products": products_db
    }


# =====================================================
# UPLOAD EXCEL FILE
# =====================================================
@router.post("/upload-products")
def upload_products(file: UploadFile = File(...)):

    try:

        # =============================================
        # CHECK FILE TYPE
        # =============================================
        if not file.filename.endswith((".xlsx", ".xls")):

            return {
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": "Only Excel files are allowed"
                }
            }

        # =============================================
        # CREATE UPLOADS FOLDER
        # =============================================
        os.makedirs("uploads", exist_ok=True)

        # =============================================
        # SAVE FILE
        # =============================================
        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # =============================================
        # READ EXCEL FILE
        # =============================================
        df = pd.read_excel(file_path)

        # =============================================
        # CHECK REQUIRED COLUMNS
        # =============================================
        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return {
                "success": False,
                "error": {
                    "code": "MISSING_COLUMNS",
                    "message": "Excel file missing required columns",
                    "missing_columns": missing_columns
                }
            }

        # =============================================
        # CHECK EMPTY CELLS
        # =============================================
        if df.isnull().values.any():

            return {
                "success": False,
                "error": {
                    "code": "EMPTY_CELLS",
                    "message": "Excel contains empty cells"
                }
            }

        # =============================================
        # CHECK NEGATIVE PRICE
        # =============================================
        if (df["Price"] < 0).any():

            return {
                "success": False,
                "error": {
                    "code": "INVALID_PRICE",
                    "message": "Negative prices are not allowed"
                }
            }

        # =============================================
        # CHECK NEGATIVE QUANTITY
        # =============================================
        if (df["Quantity"] < 0).any():

            return {
                "success": False,
                "error": {
                    "code": "INVALID_QUANTITY",
                    "message": "Negative quantities are not allowed"
                }
            }

        # =============================================
        # CONVERT EXCEL TO DICTIONARY
        # =============================================
        excel_products = df.to_dict(orient="records")

        added_products = []
        skipped_duplicates = []

        # =============================================
        # ADD PRODUCTS
        # =============================================
        for product in excel_products:

            duplicate = False

            for existing_product in products_db:

                existing_name = existing_product["name"].lower()
                new_name = product["Name"].lower()

                if existing_name == new_name:

                    duplicate = True
                    skipped_duplicates.append(product["Name"])
                    break

            # =========================================
            # SAVE PRODUCT
            # =========================================
            if not duplicate:

                formatted_product = {
                    "name": product["Name"],
                    "price": product["Price"],
                    "quantity": product["Quantity"],
                    "customer": product["Customer"]
                }

                products_db.append(formatted_product)
                added_products.append(formatted_product)

        # =============================================
        # SUCCESS RESPONSE
        # =============================================
        return {
            "success": True,
            "message": "Excel uploaded successfully",
            "added_products": len(added_products),
            "skipped_duplicates": skipped_duplicates,
            "products": added_products
        }

    # =============================================
    # UNKNOWN SERVER ERROR
    # =============================================
    except Exception as e:

        return {
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": str(e)
            }
        }