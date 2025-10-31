# petcare/api/v1/routes/users.py (VERSIÓN CORREGIDA PARA SQLALCHEMY)

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session # <-- Necesitas importar Session
# Ajusta la ruta de importación de user_schema y security si es necesario
from petcare.schemas.user_schema import UserCreate, UserOut, TokenRequest, TokenResponse
from petcare.core.security import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from petcare.core.user_services import create_user_account, get_user_by_email
from petcare.core.database import get_db # <-- IMPORTAR LA DEPENDENCIA DE LA DB

# Define el router
user_router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

# --- ENDPOINT DE REGISTRO CORREGIDO ---
@user_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db) # <-- INYECCIÓN DE LA SESIÓN DB
):
    """
    Registra un nuevo usuario (Cliente o Cuidador) en la DB real.
    """
    try:
        # Llama a la lógica de negocio, pasándole la sesión activa
        # user_services debe usar esta sesión para guardar
        new_user = create_user_account(db=db, user_data=user_data) 
        
        return new_user
    
    # Recuerda que en user_services cambiamos esto a HTTPException. 
    # Si mantuviste 'raise ValueError', esto está bien. Si usaste HTTPException, el try/except no es necesario.
    except ValueError as e: 
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
# --- ENDPOINT DE LOGIN CORREGIDO ---
@user_router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    form_data: TokenRequest,
    db: Session = Depends(get_db) # <-- INYECCIÓN DE LA SESIÓN DB
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

    # 2. Verificar Contraseña (usando la función de seguridad)
    # Debes asegurarte de importar 'verify_password' de tu security.py.
    # user.contrasena_hash es el hash almacenado en el modelo ORM (Usuario)
    from petcare.core.security import verify_password # Asegúrate de importar esto

    if not verify_password(form_data.contrasena, user.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Generar JWT de Acceso (el resto está bien)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": user.email, "user_type": user.tipo}, # <-- Usa user.tipo del ORM
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
# # petcare/api/v1/routes/users.py
# from datetime import datetime, timedelta, timezone
# from fastapi import APIRouter, HTTPException, status, Depends
# from petcare.schemas.user_schema import UserCreate, UserOut, TokenRequest, TokenResponse
# from petcare.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
# from petcare.core.user_services import create_user_account, get_user_by_email

# # Define el router
# user_router = APIRouter(
#     prefix="/users",
#     tags=["Usuarios"]
# )

# @user_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
# async def register_user(user_data: UserCreate):
#     """
#     Registra un nuevo usuario (Cliente o Cuidador).
#     """
#     try:
#         # Llama a la lógica de negocio
#         new_user = create_user_account(user_data)
        
#         # FastAPI automáticamente serializa new_user (clase de dominio) a UserOut (Pydantic)
#         return new_user
    
#     except ValueError as e:
#         # Maneja el error de unicidad de email de user_service
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT, # 409 Conflict es apropiado para un recurso duplicado
#             detail=str(e)
#         )
    
# @user_router.post("/login", response_model=TokenResponse)
# async def login_for_access_token(form_data: TokenRequest):
#     """
#     Verifica credenciales y genera un JWT de acceso.
#     """
#     # 1. Buscar y Validar Usuario
#     user = get_user_by_email(form_data.email)
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Credenciales incorrectas",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     # 2. Verificar Contraseña
#     if not user.verify_password(form_data.contrasena):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Credenciales incorrectas",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
        
#     # 3. Generar JWT de Acceso
#     # Los datos del token deben ser minimalistas (ej: solo el ID o email y tipo)
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"email": user.email, "user_type": user.user_type},
#         expires_delta=access_token_expires
#     )
    
#     return {"access_token": access_token, "token_type": "bearer"}