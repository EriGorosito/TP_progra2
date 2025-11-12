from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

# Importaciones locales
from petcare.core.database import get_db
from petcare.core.security import (
    create_access_token, 
    verify_password, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from petcare.core.user_services import create_user_account, get_user_by_email
from petcare.core.security import verify_password
from petcare.schemas.user_schema import (
    UserCreate, 
    UserOut, 
    TokenRequest, 
    TokenResponse
)


# Define el router
user_router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

   
@user_router.post(
    "/register", 
    response_model=UserOut, 
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario (Cliente o Cuidador) usando el patrón Factory.
    """
    try:
        return create_user_account(db, user_data)
   
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@user_router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    form_data: TokenRequest,
    db: Session = Depends(get_db) 
):
    """
    Verifica credenciales contra la DB y genera un JWT de acceso.
    """
    # 1. Buscar y Validar Usuario (usando el servicio con la DB)
    user = get_user_by_email(db=db, email=form_data.email) # <-- PASAR LA SESIÓN DB
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verificar Contraseña 
    if not verify_password(form_data.contrasena, user.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
       
    # 3. Generar JWT de Acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": user.email, "user_type": user.tipo}, # <-- Usa user.tipo del ORM
        expires_delta=access_token_expires
    )
   
    return {"access_token": access_token, "token_type": "bearer"}
