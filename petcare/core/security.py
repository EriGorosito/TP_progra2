# petcare/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# Importa tu servicio de usuario para buscar al usuario por email
from petcare.core.user_services import get_user_by_email
from petcare.domain.usuario import Usuario

# ⚠️ Esto debe ser una variable de entorno en producción.
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
#---
# Implementar la función de decodificación y validación de token es el siguiente paso.

# "tokenUrl" le dice a Swagger/docs que debe usar este endpoint para obtener el token.
# ¡Asegúrate de que coincida con tu ruta de login! -> /v1/users/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/users/login")

# Define un modelo Pydantic simple para los datos dentro del token
class TokenData(BaseModel):
    email: str | None = None
    user_type: str | None = None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Usuario:
    """
    Dependencia de FastAPI:
    1. Recibe un token del header "Authorization: Bearer <token>".
    2. Valida, decodifica y extrae el email.
    3. Busca al usuario en la "DB".
    4. Devuelve el objeto Usuario o lanza una excepción.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica el JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("email")
        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email, user_type=payload.get("user_type"))

    except JWTError:
        raise credentials_exception

    # Busca al usuario en la "base de datos"
    user = get_user_by_email(email=token_data.email)

    if user is None:
        raise credentials_exception

    # ¡Éxito! Devuelve el objeto de dominio del usuario
    return user