from fastapi import APIRouter, UploadFile, File
from schemas.purchase_schema import Purchase
import pandas as pd
import shutil
import os

router = APIRouter()

# =====================================================
# TEMPORARY STORAGE
# =====================================================
purchase_db = []

# =====================================================
# REQUIRED EXCEL COLUMNS
# =====================================================
required_columns = [
    "Product Name",
    "Purchase Cost",
    "Purchase Quantity",
    "Supplier Name",
    "Supplier TIN"
]

# =====================================================
# ADD SINGLE PURCHASE
# =====================================================
@router.post("/purchases")
def create_purchase(purchase: Purchase):

    # =============================================
    # CHECK DUPLICATE PRODUCT
    # =============================================
    for existing_purchase in purchase_db:

        if (
            existing_purchase["product_name"].lower()
            == purchase.product_name.lower()
        ):

            return {
                "success": False,
                "error": {
                    "code": "DUPLICATE_PRODUCT",
                    "message": f"{purchase.product_name} already exists"
                }
            }

    # =============================================
    # FORMAT PURCHASE
    # =============================================
    formatted_purchase = {
        "product_name": purchase.product_name,
        "purchase_cost": purchase.purchase_cost,
        "purchase_quantity": purchase.purchase_quantity,
        "supplier_name": purchase.supplier_name,
        "supplier_tin": purchase.supplier_tin
    }

    # =============================================
    # SAVE PURCHASE
    # =============================================
    purchase_db.append(formatted_purchase)

    return {
        "success": True,
        "message": "Purchase added successfully",
        "purchase": formatted_purchase
    }

# =====================================================
# GET ALL PURCHASES
# =====================================================
@router.get("/purchases")
def get_purchases():

    return {
        "success": True,
        "total_purchases": len(purchase_db),
        "purchases": purchase_db
    }

# =====================================================
# UPLOAD PURCHASE EXCEL FILE
# =====================================================
@router.post("/upload-purchases")
def upload_purchases(file: UploadFile = File(...)):

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
        # CHECK NEGATIVE PURCHASE COST
        # =============================================
        if (df["Purchase Cost"] < 0).any():

            return {
                "success": False,
                "error": {
                    "code": "INVALID_PURCHASE_COST",
                    "message": "Negative purchase cost is not allowed"
                }
            }

        # =============================================
        # CHECK NEGATIVE PURCHASE QUANTITY
        # =============================================
        if (df["Purchase Quantity"] < 0).any():

            return {
                "success": False,
                "error": {
                    "code": "INVALID_PURCHASE_QUANTITY",
                    "message": "Negative purchase quantity is not allowed"
                }
            }

        # =============================================
        # CONVERT EXCEL TO DICTIONARY
        # =============================================
        excel_purchases = df.to_dict(orient="records")

        added_purchases = []
        skipped_duplicates = []

        # =============================================
        # ADD PURCHASES
        # =============================================
        for purchase in excel_purchases:

            duplicate = False

            for existing_purchase in purchase_db:

                existing_name = existing_purchase[
                    "product_name"
                ].lower()

                new_name = purchase[
                    "Product Name"
                ].lower()

                if existing_name == new_name:

                    duplicate = True

                    skipped_duplicates.append(
                        purchase["Product Name"]
                    )

                    break

            # =========================================
            # SAVE PURCHASE
            # =========================================
            if not duplicate:

                formatted_purchase = {
                    "product_name": purchase["Product Name"],
                    "purchase_cost": purchase["Purchase Cost"],
                    "purchase_quantity": purchase["Purchase Quantity"],
                    "supplier_name": purchase["Supplier Name"],
                    "supplier_tin": purchase["Supplier TIN"]
                }

                purchase_db.append(formatted_purchase)

                added_purchases.append(
                    formatted_purchase
                )

        # =============================================
        # SUCCESS RESPONSE
        # =============================================
        return {
            "success": True,
            "message": "Excel uploaded successfully",
            "added_purchases": len(added_purchases),
            "skipped_duplicates": skipped_duplicates,
            "purchases": added_purchases
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