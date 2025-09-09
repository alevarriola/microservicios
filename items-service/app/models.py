from sqlalchemy import Column, Integer, String
from .db import Base

# heredamos de Base, creammos nuestra db
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    sku = Column(String(60), unique=True, index=True, nullable=False) #codigo de barra. "Stock Keeping Unit"
    stock = Column(Integer, nullable=False, default=0)