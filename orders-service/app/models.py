from sqlalchemy import Column, Integer, String
from .db import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    item_sku = Column(String(60), nullable=False)
    qty = Column(Integer, nullable=False, default=1) # quantity
    status = Column(String(20), nullable=False, default="CREATED")
