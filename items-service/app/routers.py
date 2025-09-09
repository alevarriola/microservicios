from fastapi import APIRouter, Depends, HTTPException, Body
from common.auth import verify_service_token
from common.logging import log_json
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import Base
from . import crud

router = APIRouter(tags=["items"])

# Crea tablas al importar el router
Base.metadata.create_all(bind=engine)

# manejo de sesiones de db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Validacion de lo que entrara en metodo post
class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    sku: str = Field(min_length=1, max_length=60)
    stock: int = 0

# Hereda de ItemsIn y agrega ID para el metodo get
class ItemOut(ItemIn):
    id: int


@router.get("/", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    items = crud.list_items(db)
    log_json("info", "items.listed", count=len(items))
    return items


@router.post("/", response_model=ItemOut, status_code=201)
def create_item(payload: ItemIn, db: Session = Depends(get_db)):
    try:
        item = crud.create_item(db, payload.name, payload.sku, payload.stock)
        log_json("info", "item.created", item_id=item.id, sku=item.sku, stock=item.stock)
        return item
    except ValueError as e:
        log_json("warn", "item.create.conflict", sku=payload.sku)
        raise HTTPException(status_code=409, detail=str(e))

# ruta reserve para verificar stock y existencia, descontar stock dependiendo de Orders qty    
@router.post("/reserve", response_model=ItemOut, dependencies=[Depends(verify_service_token)])
def reserve_item(sku: str = Body(..., embed=True), qty: int = Body(..., gt=0), db: Session = Depends(get_db)):
    item = crud.get_item_by_sku(db, sku)
    if not item:
        log_json("warn", "item.reserve.not_found", sku=sku)
        raise HTTPException(status_code=404, detail="Item no encontrado")
    if item.stock < qty:
        log_json("warn", "item.reserve.no_stock", sku=sku, requested=qty, available=item.stock)
        raise HTTPException(status_code=409, detail="Stock insuficiente")
    item.stock -= qty
    db.commit()
    db.refresh(item)
    log_json("info", "item.reserve.ok", item_id=item.id, new_stock=item.stock)
    return item
