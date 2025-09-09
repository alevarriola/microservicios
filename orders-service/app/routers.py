from fastapi import APIRouter, Depends, HTTPException
from common.auth import verify_service_token
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import Base
from . import crud
import httpx
import os

USERS_SERVICE_URL  = os.getenv("USERS_SERVICE_URL",  "http://127.0.0.1:8001")
ITEMS_SERVICE_URL  = os.getenv("ITEMS_SERVICE_URL",  "http://127.0.0.1:8002")

router = APIRouter(tags=["orders"])

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class OrderIn(BaseModel):
    user_id: int = Field(gt=0)
    item_sku: str = Field(min_length=1, max_length=60)
    qty: int = Field(default=1, gt=0)

class OrderOut(OrderIn):
    id: int
    status: str

@router.get("/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)

@router.post("/", response_model=OrderOut, status_code=201, dependencies=[Depends(verify_service_token)])
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    
    # Verificar usuario
    with httpx.Client() as client:
        r = client.get(f"{USERS_SERVICE_URL}/{payload.user_id}")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        r.raise_for_status()

    # Reservar stock
    with httpx.Client() as client:
        r = client.post(f"{ITEMS_SERVICE_URL}/reserve",
                        json={"sku": str(payload.item_sku), "qty": payload.qty})
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Item no encontrado")
        if r.status_code == 409:
            raise HTTPException(status_code=409, detail="Stock insuficiente")
    
    # Crear orden
    try:
        return crud.create_order(db, payload.user_id, payload.item_sku, payload.qty)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))