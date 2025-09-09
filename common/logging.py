import json, sys, time, os

SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown")

def log_json(level: str, msg: str, **kwargs):
    '''Logear en formato json'''
    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), # la convierte a string tipo 2025-09-08T00:12:34Z
        "level": level.lower(),
        "service": SERVICE_NAME,
        "msg": msg,
        **kwargs,
    }
    #mandar texto a la consola de forma manual, flush lo fuerza a mostrarse
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()
