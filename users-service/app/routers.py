from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import Base
from . import crud

router = APIRouter(tags=["users"])

# Crear tablas al importar
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=120)

class UserOut(UserIn):
    id: int

@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return crud.list_users(db)

@router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserIn, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db, payload.name, payload.email)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    u = crud.get_user_by_id(db, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u
