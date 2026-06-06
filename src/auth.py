from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

# gibt an, das  im HTTP-header nach einem feld mit diesem Namen gesucht wird
api_key_header =APIKeyHeader(name="X-API-KEY")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "password":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


