from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class SaleCreate(BaseModel):

    product_name: str
    sale_price: float
    sale_quantity: int
    customer_name: str

    customer_phone: Optional[str] = None
    customer_tin: Optional[str] = None
    customer_type: Optional[str] = None

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value):
        value = str(value).strip()

        if not value:
            raise ValueError("Product name cannot be empty")

        return value

    @field_validator("sale_price")
    @classmethod
    def validate_sale_price(cls, value):
        if value <= 0:
            raise ValueError("Sale price must be greater than 0")

        return value

    @field_validator("sale_quantity")
    @classmethod
    def validate_sale_quantity(cls, value):
        if value <= 0:
            raise ValueError("Sale quantity must be greater than 0")

        return value

    @field_validator("customer_phone")
    @classmethod
    def validate_phone(cls, value):

        if value is None:
            return value

        value = str(value).strip()

        if not value.isdigit():
            raise ValueError("Customer phone must contain only numbers")

        if len(value) != 9:
            raise ValueError("Customer phone must be exactly 9 digits")

        if value.startswith("0"):
            raise ValueError("Phone must not start with 0")

        return value

    @field_validator("customer_tin")
    @classmethod
    def validate_tin(cls, value):

        if value is None:
            return value

        value = str(value).strip()

        if not value.isdigit():
            raise ValueError("Customer TIN must contain only numbers")

        if len(value) != 9:
            raise ValueError("Customer TIN must be exactly 9 digits")

        return value

    @model_validator(mode="after")
    def validate_customer(self):

        if not self.customer_phone and not self.customer_tin:
            raise ValueError(
                "Provide Customer Phone or Customer TIN"
            )

        if self.customer_tin:
            self.customer_type = "company"
        else:
            self.customer_type = "personal"

        return self