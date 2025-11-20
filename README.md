# Microservicios con FastAPI

Pequeño ecosistema de **microservicios en Python** pensado para practicar:

- Diseño de servicios independientes (usuarios, ítems, órdenes).
- Uso de **FastAPI** + **Uvicorn**.
- Comunicación entre servicios vía HTTP con:
  - Auth interna mediante cabecera `X-Service-Token`.
  - Cliente HTTP con **reintentos** y **circuit breaker** simple.
- Persistencia local con **SQLite + SQLAlchemy**.
- Gateway HTTP que unifica el acceso desde el cliente.

---

## Descripción general

El proyecto está compuesto por **4 aplicaciones FastAPI**:

- **API Gateway** (`gateway/`): punto de entrada único. Expone `/users`, `/items` y `/orders` y reenvía las peticiones al microservicio correspondiente.
- **Users Service** (`users-service/`): maneja usuarios (CRUD sencillo).
- **Items Service** (`items-service/`): maneja ítems de inventario (CRUD + stock).
- **Orders Service** (`orders-service/`): crea órdenes y coordina con `users-service` e `items-service` para validar usuario y stock.

Además, hay un paquete compartido **`common/`** con:

- `auth.py` – autenticación entre servicios vía header `X-Service-Token`.
- `http.py` – cliente HTTP con **circuit breaker** y reintentos.
- `logging.py` – logs en formato JSON con el nombre del servicio.

Es un proyecto ideal para usar en clases o como base para experimentar con patrones de microservicios sin necesitar Docker ni infraestructura pesada.

---

## Arquitectura

```text
[ Cliente ]
    |
    v
[ API Gateway ]  (http://localhost:8080)
   |     |        |     |         |     | 
   v     v        v     v         v     v
[Users Service]  [Items Service]  [Orders Service]
   8001             8002              8003
   users.db         items.db          orders.db
```

- El **Gateway** recibe todas las peticiones y las redirige usando `httpx.AsyncClient`.
- Los servicios se hablan entre sí usando URLs internas (`USERS_SERVICE_URL`, `ITEMS_SERVICE_URL`) y agregan un token compartido en la cabecera `X-Service-Token`.
- El módulo `common.http` mantiene un pequeño estado en memoria para saber cuántos fallos hubo contra cada host y "abrir" el circuito por unos segundos si un servicio falla demasiado.

---

## Stack técnico

- **Lenguaje:** Python 3.11+ (recomendado)
- **Framework web:** FastAPI
- **Servidor ASGI:** Uvicorn
- **Cliente HTTP:** httpx
- **ORM:** SQLAlchemy 2.x
- **Base de datos:** SQLite (archivos locales `data/*.db`)
- **Validación:** Pydantic v2
- **Scripts:** PowerShell (`run.ps1`) para levantar todo en Windows

Dependencias clave (ver `requirements.txt`):

```txt
fastapi
uvicorn[standard]
httpx
sqlalchemy
pydantic
python-dotenv
```

---

## Estructura del proyecto

```text
microservicios/
├─ common/
│  ├─ __init__.py
│  ├─ auth.py        # Header X-Service-Token y verificación
│  ├─ http.py        # Cliente HTTP + circuit breaker
│  └─ logging.py     # Logs JSON con SERVICE_NAME
│
├─ gateway/
│  └─ app/
│     ├─ __init__.py
│     ├─ main.py     # FastAPI + proxy /users, /items, /orders
│     └─ settings.py # URLs de los servicios
│
├─ users-service/
│  └─ app/
│     ├─ __init__.py
│     ├─ db.py       # Engine SQLite data/users.db
│     ├─ models.py   # Modelo User
│     ├─ crud.py     # Operaciones sobre usuarios
│     └─ routers.py  # Endpoints FastAPI
│
├─ items-service/
│  └─ app/
│     ├─ __init__.py
│     ├─ db.py       # Engine SQLite data/items.db
│     ├─ models.py   # Modelo Item
│     ├─ crud.py     # Operaciones sobre ítems y stock
│     └─ routers.py  # Endpoints FastAPI (CRUD + endpoints internos)
│
├─ orders-service/
│  └─ app/
│     ├─ __init__.py
│     ├─ db.py       # Engine SQLite data/orders.db
│     ├─ models.py   # Modelo Order
│     ├─ crud.py     # Creación y listado de órdenes
│     └─ routers.py  # Endpoints FastAPI, orquestación de usuarios/ítems
│
├─ requirements.txt
└─ run.ps1           # Script para levantar todo en Windows
```

---

## ⚙Configuración

### Variables de entorno

Algunos valores se pueden configurar vía variables de entorno:

- `SERVICE_SECRET`  
  Token compartido entre servicios.  
  - Por defecto: `"dev-secret"`.
  - Se usa para:
    - Firmar el header `X-Service-Token` en llamadas entre servicios (`add_service_auth`).
    - Validar el token entrante (`verify_service_token`).

- `USERS_SERVICE_URL`, `ITEMS_SERVICE_URL`, `ORDERS_SERVICE_URL`  
  URLs internas de cada servicio.  
  - Por defecto (modo local):
    - `USERS_SERVICE_URL = http://127.0.0.1:8001`
    - `ITEMS_SERVICE_URL = http://127.0.0.1:8002`
    - `ORDERS_SERVICE_URL = http://127.0.0.1:8003`

El **Gateway** y el **Orders Service** leen estas URLs para saber a dónde llamar.

Puedes crear un archivo `.env` en la raíz (o configurar las variables en tu sistema) si querés usar otros puertos o nombres de host.

---

## Puesta en marcha (local)

### 1. Clonar el repositorio

```bash
git clone <URL-del-repo>
cd microservicios-main
```

> Si lo descargaste como ZIP, el directorio puede llamarse algo como `microservicios-main/`.

### 2. Crear entorno virtual

```bash
python -m venv .venv

# En Linux/macOS
source .venv/bin/activate

# En Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Levantar los servicios

#### Opción A — Windows (PowerShell) con `run.ps1`

```bash
.
un.ps1
```

El script:

- Activa `.venv`.
- Abre 4 ventanas de PowerShell, cada una ejecutando:

  - `uvicorn users-service.app.main:app --reload --port 8001`
  - `uvicorn items-service.app.main:app --reload --port 8002`
  - `uvicorn orders-service.app.main:app --reload --port 8003`
  - `uvicorn gateway.app.main:app --reload --port 8080`

#### Opción B — Manual (cualquier sistema)

En 4 terminales distintas:

```bash
# 1) Users Service
uvicorn users-service.app.main:app --reload --port 8001

# 2) Items Service
uvicorn items-service.app.main:app --reload --port 8002

# 3) Orders Service
uvicorn orders-service.app.main:app --reload --port 8003

# 4) API Gateway
uvicorn gateway.app.main:app --reload --port 8080
```

---

## Salud de servicios

Cada servicio expone un endpoint de health-check:

- Gateway: `GET http://localhost:8080/health`
- Users Service: `GET http://localhost:8001/health`
- Items Service: `GET http://localhost:8002/health`
- Orders Service: `GET http://localhost:8003/health`

Además, en `startup` cada servicio loguea un evento `service.started` en formato JSON (útil si luego se envía a un sistema de logs centralizado).

---

## Auth entre servicios

El módulo `common/auth.py` implementa **autenticación simple de servicio a servicio**:

- Función `add_service_auth(headers)`:
  - Devuelve una copia de los headers agregando `"X-Service-Token": SERVICE_SECRET`.
  - La usa el Gateway y el Orders Service antes de llamar a otros servicios.

- Función `verify_service_token(...)`:
  - Se declara como dependencia en los routers que deben ser accedidos sólo por otros servicios.
  - Si el header no coincide con `SERVICE_SECRET`, lanza un `HTTPException(401)`.

Esto permite que ciertos endpoints (por ejemplo, los que modifican stock) no estén expuestos a clientes externos, sólo a otros microservicios confiables.

---

## Gateway HTTP

El **API Gateway** (`gateway/app/main.py`) expone:

- `GET /` → mensaje simple `"Gateway listo"`.
- `GET /health` → estado del gateway.
- Rutas proxy:
  - `/users{path:path}` → hacia `USERS_SERVICE_URL`.
  - `/items{path:path}` → hacia `ITEMS_SERVICE_URL`.
  - `/orders{path:path}` → hacia `ORDERS_SERVICE_URL`.

La función interna `_proxy`:

1. Lee método, headers, body y query string del request.
2. Agrega el header `X-Service-Token` con `add_service_auth`.
3. Llama al servicio correspondiente con `httpx.AsyncClient`.
4. Devuelve al cliente final la respuesta (status code, body y `content-type` original).

Desde el punto de vista del cliente, todo se maneja contra `http://localhost:8080`.

---

## Servicios

### Users Service (`users-service`)

- Base de datos: `sqlite:///data/users.db`.
- Modelo `User`:
  - `id: int`
  - `name: str`
  - `email: str` (único)
- Endpoints principales (resumen):

  - `GET /users/` – listar usuarios.
  - `POST /users/` – crear usuario.
  - `GET /users/{user_id}` – obtener usuario por id.
  - `PUT /users/{user_id}` – actualizar nombre/email.
  - `DELETE /users/{user_id}` – eliminar usuario.

- Validaciones:
  - Email único (si se repite, devuelve 409).
  - Errores de "no encontrado" devuelven 404.

### Items Service (`items-service`)

- Base de datos: `sqlite:///data/items.db`.
- Modelo `Item`:
  - `id: int`
  - `name: str`
  - `sku: str` (único)
  - `stock: int`
- Endpoints (resumen):

  - `GET /items/` – listar ítems.
  - `POST /items/` – crear ítem.
  - `GET /items/{item_id}` – obtener ítem por id.
  - `PUT /items/{item_id}` – actualizar nombre/sku/stock.
  - `DELETE /items/{item_id}` – eliminar ítem.
  - (Más endpoints internos protegidos por `verify_service_token` para validar y reservar stock desde otros servicios).

- Validaciones:
  - SKU único (409 si se repite).
  - Manejo de 404 para ítems inexistentes.

### Orders Service (`orders-service`)

- Base de datos: `sqlite:///data/orders.db`.
- Modelo `Order`:
  - `id: int`
  - `user_id: int`
  - `item_sku: str`
  - `qty: int`
  - `status: str` (por defecto `"CREATED"`)

- Endpoints (resumen):

  - `GET /orders/` – listar órdenes.
  - `POST /orders/` – crear nueva orden (punto interesante):

    1. Llama al **Users Service** para verificar que el usuario exista.
    2. Llama al **Items Service** para chequear stock del SKU y reservarlo.
    3. Si todo sale bien, crea el registro en la base de datos local.
    4. Loguea eventos JSON (`order.created`, `user.not_found`, `item.no_stock`, etc.).

- En caso de problemas:
  - Usuario inexistente → 404.
  - Ítem inexistente → 404.
  - Stock insuficiente → 409.
  - Cualquier otro error → 400 con detalle.

- Las llamadas HTTP a otros servicios utilizan el módulo `common.http`, que implementa:
  - Reintentos con pequeño backoff.
  - Contador de fallos por host.
  - "Circuit breaker" que deja de llamar a un servicio unos segundos si falló muchas veces seguidas.

---

## Autor

**Alejandro Arriola**  
Programador en constante formacion.

- GitHub: [@alevarriola](https://github.com/alevarriola)

