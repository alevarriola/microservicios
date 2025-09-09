import httpx, time

# Estado en memoria para breaker
_failures = {}
_open_until = {}
MAX_FAILS = 3         # cuántos fallos antes de abrir breaker
COOLDOWN = 10         # segundos que queda abierto el breaker

# Verifica si el breaker esta abierto
def _is_open(host: str) -> bool:
    until = _open_until.get(host, 0)
    return time.time() < until

# Suma fallos, si alcanzamos el maximo abrimos el breaker
def _record_failure(host: str):
    _failures[host] = _failures.get(host, 0) + 1
    if _failures[host] >= MAX_FAILS:
        _open_until[host] = time.time() + COOLDOWN
        _failures[host] = 0  # resetea contador

# si el request es exitoso, limpiamos variables
def _record_success(host: str):
    _failures[host] = 0
    _open_until[host] = 0


def request(method: str, url: str, **kwargs):
    """Cliente con timeout, retry y mini breaker."""
    host = url.split("/")[2]  

    # si el breaker esta abierto, no intentar llamar
    if _is_open(host):
        raise RuntimeError(f"Circuit breaker abierto para {host}")

    # intentamos 3 veces
    tries = 0
    last_exc = None
    while tries < 3:
        tries += 1
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.request(method, url, **kwargs)
                resp.raise_for_status()
                _record_success(host)
                return resp
        except Exception as e:
            last_exc = e
            _record_failure(host)
            time.sleep(0.5 * tries)  # backoff 
    raise last_exc
