from fastapi import APIRouter, UploadFile, File
from schemas.sale_schema import Sale
import pandas as pd
import os

router = APIRouter()

# =====================================================
# TEMP STORAGE (replace with DB later)
# =====================================================
sale_db = []

# =====================================================
# REQUIRED COLUMNS
# =====================================================
required_columns = [
    "Product Name",
    "Sale Price",
    "Sale Quantity",
    "Customer Name"
]

# =====================================================
# FILE HELPERS
# =====================================================
def validate_file_type(filename: str):
    return filename.endswith((".xlsx", ".xls"))


def save_file(file: UploadFile):
    os.makedirs("uploads", exist_ok=True)
    path = f"uploads/{file.filename}"

    with open(path, "wb") as buffer:
        buffer.write(file.file.read())

    return path


# =====================================================
# CLEAN VALUES (IMPORTANT)
# =====================================================
def clean_value(v):
    if v is None:
        return None
    if pd.isna(v):
        return None

    v = str(v).strip()
    if v.lower() in ["nan", "none", "null", ""]:
        return None

    return v


# =====================================================
# NORMALIZE COLUMNS
# =====================================================
def normalize_columns(df: pd.DataFrame):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("_", " ")
        .str.title()
    )
    return df


# =====================================================
# VALIDATION: PHONE (STRICT 9 DIGITS)
# =====================================================
def validate_phone(phone):
    phone = clean_value(phone)

    if phone is None:
        return None

    if not phone.isdigit():
        raise ValueError(f"Customer Phone must be numeric: {phone}")

    if len(phone) != 9:
        raise ValueError(f"Customer Phone must be exactly 9 digits: {phone}")

    if phone.startswith("0"):
        raise ValueError(f"Customer Phone must not start with 0: {phone}")

    return phone


# =====================================================
# VALIDATION: TIN (STRICT 9 DIGITS)
# =====================================================
def validate_tin(tin):
    tin = clean_value(tin)

    if tin is None:
        return None

    if not tin.isdigit():
        raise ValueError(f"Customer TIN must be numeric: {tin}")

    if len(tin) != 9:
        raise ValueError(f"Customer TIN must be exactly 9 digits: {tin}")

    return tin


# =====================================================
# CREATE SINGLE SALE
# =====================================================
@router.post("/sales")
def create_sale(sale: Sale):

    data = sale.model_dump()
    sale_db.append(data)

    return {
        "success": True,
        "message": "Sale created successfully",
        "sale": data
    }


# =====================================================
# GET ALL SALES
# =====================================================
@router.get("/sales")
def get_sales():

    return {
        "success": True,
        "total_sales": len(sale_db),
        "sales": sale_db
    }


# =====================================================
# UPLOAD SALES EXCEL (STRICT + SAFE)
# =====================================================
@router.post("/upload-sales")
def upload_sales(file: UploadFile = File(...)):

    try:
        # 1. Validate file type
        if not validate_file_type(file.filename):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": "Only Excel files allowed"
                }
            }

        # 2. Save file
        path = save_file(file)

        # 3. Read Excel
        df = pd.read_excel(path, dtype=str)

        # 4. Normalize columns
        df = normalize_columns(df)

        # 5. Clean NaN
        df = df.where(pd.notnull(df), None)

        # 6. Validate required columns
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            return {
                "success": False,
                "error": {
                    "code": "MISSING_COLUMNS",
                    "message": "Missing required columns",
                    "missing_columns": missing
                }
            }

        # 7. Must have at least one contact column
        if "Customer Phone" not in df.columns and "Customer TIN" not in df.columns:
            return {
                "success": False,
                "error": {
                    "code": "MISSING_CUSTOMER_INFO",
                    "message": "Provide Customer Phone or Customer TIN"
                }
            }

        records = df.to_dict(orient="records")

        added = []
        errors = []

        # 8. Process rows
        for i, row in enumerate(records, start=1):

            try:
                phone = validate_phone(row.get("Customer Phone"))
                tin = validate_tin(row.get("Customer TIN"))

                # Must have at least one valid contact
                if not phone and not tin:
                    errors.append({
                        "row": i,
                        "field": "customer_contact",
                        "error": "Provide valid 9-digit Customer Phone or TIN"
                    })
                    continue

                customer_type = "company" if tin else "personal"

                sale_data = {
                    "product_name": clean_value(row.get("Product Name")),
                    "sale_price": float(row.get("Sale Price") or 0),
                    "sale_quantity": int(row.get("Sale Quantity") or 0),
                    "customer_name": clean_value(row.get("Customer Name")),
                    "customer_phone": phone,
                    "customer_tin": tin,
                    "customer_type": customer_type
                }

                # FINAL schema validation (important safety layer)
                sale_obj = Sale(**sale_data)

                final = sale_obj.model_dump()

                sale_db.append(final)
                added.append(final)

            except Exception as e:
                errors.append({
                    "row": i,
                    "error": str(e)
                })

        # 9. Return response
        if errors:
            return {
                "success": False,
                "message": "Some rows failed validation",
                "added_sales": len(added),
                "errors": errors,
                "sales": added
            }

        return {
            "success": True,
            "message": "Sales uploaded successfully",
            "added_sales": len(added),
            "sales": added
        }

    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": str(e)
            }
        }