# Activa el entorno virtual
. .venv/Scripts/Activate.ps1

# Levanta cada servicio en su terminal
Start-Process powershell -ArgumentList "uvicorn users-service.app.main:app --reload --port 8001"
Start-Process powershell -ArgumentList "uvicorn items-service.app.main:app --reload --port 8002"
Start-Process powershell -ArgumentList "uvicorn gateway.app.main:app --reload --port 8080"
