import os
from fastapi import FastAPI
from .routers import router
from common.logging import log_json

os.environ["SERVICE_NAME"] = "users"

app = FastAPI(title="Users Service")
app.include_router(router)

@app.on_event("startup")
def startup():
    log_json("info", "service.started")

@app.get("/health")
def health():
    log_json("info", "health.check")
    return {"status": "ok"}
