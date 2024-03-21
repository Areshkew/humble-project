from datetime import timedelta, datetime, timezone
from fastapi import HTTPException, status
import jwt, pathlib

PUBLIC_KEY = pathlib.Path("keys/public_key.pem").read_text(encoding='utf-8')
PRIVATE_KEY = pathlib.Path("keys/private_key.pem").read_text(encoding='utf-8')
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_token(payload: dict):
    data = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({
            "exp": expire
        })
    
    token = jwt.encode(payload=data, key=PRIVATE_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(jwt=token, key=PUBLIC_KEY, algorithms=ALGORITHM)

    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "No se pudieron validar los credenciales.",
                            headers={"WWW-Authenticate": "Bearer"})
    return payload