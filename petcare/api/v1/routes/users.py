# petcare/api/v1/routes/users.py
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from petcare.schemas.user_schema import UserCreate, UserOut, TokenRequest, TokenResponse
from petcare.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from petcare.core.user_services import create_user_account, get_user_by_email

# Define el router
user_router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

@user_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Registra un nuevo usuario (Cliente o Cuidador).
    """
    try:
        # Llama a la lógica de negocio
        new_user = create_user_account(user_data)
        
        # FastAPI automáticamente serializa new_user (clase de dominio) a UserOut (Pydantic)
        return new_user
    
    except ValueError as e:
        # Maneja el error de unicidad de email de user_service
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict es apropiado para un recurso duplicado
            detail=str(e)
        )
    
@user_router.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: TokenRequest):
    """
    Verifica credenciales y genera un JWT de acceso.
    """
    # 1. Buscar y Validar Usuario
    user = get_user_by_email(form_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verificar Contraseña
    if not user.verify_password(form_data.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Generar JWT de Acceso
    # Los datos del token deben ser minimalistas (ej: solo el ID o email y tipo)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": user.email, "user_type": user.user_type},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}