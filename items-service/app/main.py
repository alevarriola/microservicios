from fastapi import FastAPI
from .routers import router

app = FastAPI(title="Items Service")
app.include_router(router)   # expone GET/POST en "/"

@app.get("/health")
def health():
    return {"status": "ok"}
