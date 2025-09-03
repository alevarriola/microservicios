from sqlalchemy.orm import Session
from .models import Order

def list_orders(db: Session):
    return db.query(Order).all()

def create_order(db: Session, user_id: int, item_id: int, qty: int = 1, status: str = "CREATED"):
    o = Order(user_id=user_id, item_id=item_id, qty=qty, status=status)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o
