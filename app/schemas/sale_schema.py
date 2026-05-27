from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class Sale(BaseModel):

    product_name: str
    sale_price: float
    sale_quantity: int
    customer_name: str

    customer_phone: Optional[str] = None
    customer_tin: Optional[str] = None
    customer_type: Optional[str] = None  # auto-generated

    # =========================
    # PRODUCT NAME
    # =========================
    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Product name cannot be empty")
        return value

    # =========================
    # SALE PRICE
    # =========================
    @field_validator("sale_price")
    @classmethod
    def validate_sale_price(cls, value):
        if value <= 0:
            raise ValueError("Sale price must be greater than 0")
        return value

    # =========================
    # SALE QUANTITY
    # =========================
    @field_validator("sale_quantity")
    @classmethod
    def validate_sale_quantity(cls, value):
        if value <= 0:
            raise ValueError("Sale quantity must be greater than 0")
        return value

    # =========================
    # CUSTOMER NAME
    # =========================
    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Customer name cannot be empty")
        return value

    # =========================
    # PHONE VALIDATION (MAX 9 DIGITS)
    # =========================
    @field_validator("customer_phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value

        value = str(value).strip()

        if not value.isdigit():
            raise ValueError("Customer phone must contain only numbers")

        # 🔥 FIX: must NOT exceed 9 digits
        if len(value) > 9:
            raise ValueError("Customer phone must not exceed 9 digits")

        # still enforce exact format if you want strict system
        if len(value) != 9:
            raise ValueError("Customer phone must be exactly 9 digits")

        if value.startswith("0"):
            raise ValueError("Phone must not start with 0 (e.g. 787182343)")

        return value

    # =========================
    # TIN VALIDATION (MAX 9 DIGITS)
    # =========================
    @field_validator("customer_tin")
    @classmethod
    def validate_tin(cls, value):
        if value is None:
            return value

        value = str(value).strip()

        if not value.isdigit():
            raise ValueError("Customer TIN must contain only numbers")

        # 🔥 FIX: must NOT exceed 9 digits
        if len(value) > 9:
            raise ValueError("Customer TIN must not exceed 9 digits")

        # still enforce exact 9-digit rule
        if len(value) != 9:
            raise ValueError("Customer TIN must be exactly 9 digits")

        return value

    # =========================
    # BUSINESS RULES
    # =========================
    @model_validator(mode="after")
    def validate_customer_rule(self):

        if not self.customer_phone and not self.customer_tin:
            raise ValueError("Provide Customer Phone or Customer TIN")

        if self.customer_tin:
            self.customer_type = "company"
        else:
            self.customer_type = "personal"

        return self