from fastapi import FastAPI

app = FastAPI(title="Orders Service")

@app.get("/")
def root():
    return {"message": "Hello World desde Orders Service"}

@app.get("/health")
def health():
    return {"status": "ok"}
