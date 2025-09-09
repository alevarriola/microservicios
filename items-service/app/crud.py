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

# metodo PUT
def get_item_by_id(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

def update_item(db: Session, item_id: int, name: str | None = None, sku: str | None = None, stock: int | None = None):
    item = get_item_by_id(db, item_id)
    if not item:
        return None
    if sku and db.query(Item).filter(Item.sku == sku, Item.id != item_id).first():
        raise ValueError("SKU ya existente")
    if name is not None:  item.name = name
    if sku  is not None:  item.sku  = sku
    if stock is not None: item.stock = stock
    db.commit(); db.refresh(item)
    return item

# metodo DELETE
def delete_item(db: Session, item_id: int) -> bool:
    item = get_item_by_id(db, item_id)
    if not item:
        return False
    db.delete(item); db.commit()
    return True