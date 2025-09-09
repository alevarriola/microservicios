import os
from fastapi import FastAPI
from .routers import router
from common.logging import log_json

# definimos que es el servicio items en variable de entorno
os.environ["SERVICE_NAME"] = "items"

# iniciamos fastapi y agregamos endpoints
app = FastAPI(title="Items Service")
app.include_router(router)

# gancho de prendido (obsoleto)
@app.on_event("startup")
def startup():
    log_json("info", "service.started")

# verificacion si todo esta bien
@app.get("/health")
def health():
    log_json("info", "health.check")
    return {"status": "ok"}

