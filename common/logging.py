import json, sys, time, os

SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown")

def log_json(level: str, msg: str, **kwargs):
    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level.lower(),
        "service": SERVICE_NAME,
        "msg": msg,
        **kwargs,
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()
