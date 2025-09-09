from fastapi import APIRouter, Depends, HTTPException
from common.auth import verify_service_token, add_service_auth
from common.logging import log_json
from common import http
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import Base
from . import crud
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
    qty: int = Field(default=1, gt=0) # greater than

class OrderOut(OrderIn):
    id: int
    status: str

@router.get("/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    orders = crud.list_orders(db)
    log_json("info", "orders.listed", count=len(orders))
    return orders

@router.post("/", response_model=OrderOut, status_code=201, dependencies=[Depends(verify_service_token)])
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    
    #Verificar que usuario exista
    try:
         r = http.request(
            "GET",
            f"{USERS_SERVICE_URL}/{payload.user_id}",
            headers=add_service_auth({})  
        )
    except RuntimeError as e:
        log_json("error", "user.service.unavailable", user_id=payload.user_id)
        raise HTTPException(status_code=503, detail=str(e))
    if r.status_code == 404:
        log_json("warn", "user.not_found", user_id=payload.user_id)
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    #Verificar reserva de stock
    try:
       r = http.request(
            "POST",
            f"{ITEMS_SERVICE_URL}/reserve",
            json={"sku": payload.item_sku, "qty": payload.qty}, 
            headers=add_service_auth({})  
        )
    except RuntimeError as e:
        log_json("error", "item.service.unavailable", item_sku=payload.item_sku)
        raise HTTPException(status_code=503, detail=str(e))
    if r.status_code == 404:
        log_json("warn", "item.not_found", item_sku=payload.item_sku)
        raise HTTPException(status_code=404, detail="Item no encontrado")
    if r.status_code == 409:
        log_json("warn", "item.no_stock", item_sku=payload.item_sku, requested=payload.qty)
        raise HTTPException(status_code=409, detail="Stock insuficiente")

    #Si todo sale bien, Crear orden
    try:
        order = crud.create_order(db, payload.user_id, payload.item_sku, payload.qty)
        log_json("info", "order.created", order_id=order.id, user_id=order.user_id, item_sku=order.item_sku, qty=order.qty)
        return order
    except Exception as e:
        log_json("error", "order.create.failed", user_id=payload.user_id, item_sku=payload.item_sku)
        raise HTTPException(status_code=400, detail=str(e))