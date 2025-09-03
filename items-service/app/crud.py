from sqlalchemy.orm import Session
from .models import Item

# metodo GET
def list_items(db: Session):
    return db.query(Item).all()

def get_item_by_sku(db: Session, sku: str):
    return db.query(Item).filter(Item.sku == sku).first()

# metodo POST
def create_item(db: Session, name: str, sku: str, stock: int = 0):
    # Validación simple de SKU único
    if get_item_by_sku(db, sku):
        raise ValueError("SKU ya existente")
    item = Item(name=name, sku=sku, stock=stock)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
