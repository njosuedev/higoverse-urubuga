from pydantic import BaseModel, Field, field_validator

class Purchase(BaseModel):
    product_name: str
    purchase_cost: float
    purchase_quantity: int
    supplier_name: str

    supplier_tin: str = Field(
        ...,
        min_length=9,
        max_length=9
    )

    @field_validator("supplier_tin")
    @classmethod
    def validate_tin(cls, value):

        if not value.isdigit():
            raise ValueError(
                "Supplier TIN must contain only numbers"
            )

        if len(value) != 9:
            raise ValueError(
                "Supplier TIN must be exactly 9 digits"
            )

        return value