# petcare/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError

# ⚠️ ¡IMPORTANTE! Esto debe ser una variable de entorno en producción.
# Usaremos una simple para el MOCK.
SECRET_KEY = "SUPER_SECRETO_PARA_PRUEBAS_NO_USAR_EN_PROD" 
ALGORITHM = "HS256" # Algoritmo de hashing para el token

# Define cuánto durará el token antes de expirar (ej: 15 minutos)
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Genera un JWT de acceso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload del token: incluye la expiración y los datos del usuario (subject)
    to_encode.update({"exp": expire, "sub": str(data["email"])})
    
    # Crea el token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Implementar la función de decodificación y validación de token es el siguiente paso.