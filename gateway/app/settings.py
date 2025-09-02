import os

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://127.0.0.1:8001")
ITEMS_SERVICE_URL = os.getenv("ITEMS_SERVICE_URL", "http://127.0.0.1:8002")