from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base


class SaleModel(Base):

    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)

    product_name = Column(String)
    sale_price = Column(Float)
    sale_quantity = Column(Integer)

    customer_name = Column(String)
    customer_phone = Column(String)
    customer_tin = Column(String)
    customer_type = Column(String)