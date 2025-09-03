from fastapi import FastAPI
from .routers import router

app = FastAPI(title="Users Service")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
