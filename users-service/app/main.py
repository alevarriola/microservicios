from fastapi import FastAPI

app = FastAPI(title="Users Service")

@app.get("/")
def root():
    return {"message": "Hello World desde Users Service"}

@app.get("/health")
def health():
    return {"status": "ok"}
