from fastapi import APIRouter, Depends, HTTPException
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
    return crud.list_items(db)


@router.post("/", response_model=ItemOut, status_code=201)
def create_item(payload: ItemIn, db: Session = Depends(get_db)):
    try:
        return crud.create_item(db, payload.name, payload.sku, payload.stock)
    except ValueError as e:
        # SKU duplicado
        raise HTTPException(status_code=409, detail=str(e))
