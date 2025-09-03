from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite local
DATABASE_URL = "sqlite:///data/items.db"

# Motor de db
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # necesario para SQLite + threads en dev
)

# Instamciamos la sesion
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# creamos la Base de la db
class Base(DeclarativeBase):
    pass
