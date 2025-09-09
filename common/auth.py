# common/auth.py
import os
from fastapi import Header, HTTPException

SECRET = os.getenv("SERVICE_SECRET", "dev-secret")

def add_service_auth(headers: dict) -> dict:
    """Agrega el token secreto a los headers antes de llamar otro servicio."""
    headers = headers.copy()
    headers["X-Service-Token"] = SECRET
    return headers

def verify_service_token(x_service_token: str = Header(default=None)):
    """Verifica que el request entrante tenga el token secreto correcto."""
    if x_service_token != SECRET:
        raise HTTPException(status_code=401, detail="Invalid service token")
