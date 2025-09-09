from fastapi import FastAPI, Request, Response
import httpx
from .settings import USERS_SERVICE_URL, ITEMS_SERVICE_URL, ORDERS_SERVICE_URL
from common.auth import add_service_auth

app = FastAPI(title="API Gateway")

@app.get("/")
def root():
    return {"message": "Gateway listo"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Proxy hacia users-service
@app.api_route("/users{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def users_proxy(request: Request, path: str = ""):
    url = f"{USERS_SERVICE_URL}{path or '/'}"
    return await _proxy(request, url)

# Proxy hacia items-service
@app.api_route("/items{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def items_proxy(request: Request, path: str = ""):
    url = f"{ITEMS_SERVICE_URL}{path or '/'}"
    return await _proxy(request, url)

# Proxy hacia orders-service
@app.api_route("/orders{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def orders_proxy(request: Request, path: str = ""):
    url = f"{ORDERS_SERVICE_URL}{path or '/'}"
    return await _proxy(request, url)

async def _proxy(request: Request, url: str):
    # Guardamos el Get/Post
    method = request.method

    # Pasamos headers y body originales, al headers añadimos autenticacion interna
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    headers = add_service_auth(headers)
    body = await request.body()

    # Incluimos querystring
    qs = request.url.query
    if qs:
        url = f"{url}?{qs}"

    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=headers, content=body)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type")
    )
