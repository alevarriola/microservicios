from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import Base
from . import crud
from common.logging import log_json

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

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(min_length=None, max_length=120)

@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = crud.list_users(db)
    log_json("info", "users.listed", count=len(users))
    return crud.list_users(db)

@router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserIn, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, payload.name, payload.email)
        log_json("info", "user.created", user_id=user.id, email=user.email)
        return user
    except ValueError as e:
        log_json("warn", "user.create.conflict", email=payload.email)
        raise HTTPException(status_code=409, detail=str(e))
    
@router.get("/{user_id}", response_model=UserOut, summary="Obtener usuario por ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    u = crud.get_user_by_id(db, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u

@router.put("/{user_id}", response_model=UserOut, summary="Actualizar usuario")
def update_user_route(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    try:
        u = crud.update_user(db, user_id, payload.name, payload.email)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u

@router.delete("/{user_id}", status_code=204, summary="Eliminar usuario")
def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Response(status_code=204)
