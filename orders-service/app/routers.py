from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import Base
from . import crud

router = APIRouter(tags=["orders"])

# Crear tablas al importar
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class OrderIn(BaseModel):
    user_id: int = Field(gt=0)
    item_id: int = Field(gt=0)
    qty: int = Field(default=1, gt=0)

class OrderOut(OrderIn):
    id: int
    status: str

@router.get("/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)

@router.post("/", response_model=OrderOut, status_code=201)
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    try:
        return crud.create_order(db, payload.user_id, payload.item_id, payload.qty)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
