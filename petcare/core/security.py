from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBearer, 
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer
)
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext 
from sqlalchemy.orm import Session

#Importaciones locales
from petcare.core.database import get_db

# --- CONFIGURACIÓN DE SEGURIDAD ---
SECRET_KEY = "SUPER_SECRETO_PARA_PRUEBAS_NO_USAR_EN_PROD" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# --- HASHING DE CONTRASEÑA ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hashea la contraseña."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña plana contra el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)


# --- GENERACIÓN Y VALIDACIÓN DE JWT ---
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

# Define un modelo Pydantic simple para los datos dentro del token
class TokenData(BaseModel):
    email: str | None = None
    user_type: str | None = None

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db) 
):
    """
    Dependencia de FastAPI:
    1. Recibe un token del header "Authorization: Bearer <token>".
    2. Valida, decodifica y extrae el email.
    3. Busca al usuario en la "DB".
    4. Devuelve el objeto Usuario o lanza una excepción.
    """
    # Evita importacion circular
    from petcare.core.user_services import get_user_by_email 

    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email, user_type=payload.get("tipo"))

        user = get_user_by_email(db=db, email=token_data.email) 
        
        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception

    finally:
        if db:
            db.close()

