from sqlalchemy.orm import Session
from .models import User

def list_users(db: Session):
    return db.query(User).all()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, name: str, email: str):
    if get_user_by_email(db, email):
        raise ValueError("Email ya registrado")
    u = User(name=name, email=email)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
