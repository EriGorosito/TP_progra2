
from pydantic import BaseModel, EmailStr
from typing import Literal

# Modelo Pydantic para los datos que el usuario envía al registrarse
class UserCreate(BaseModel):
    # Usamos EmailStr para una validación de formato automática
    email: EmailStr
    # El nombre ahora es un campo de entrada
    nombre: str
    # En un API real, se manejaría de forma más segura (ej. no retornarla)
    contrasena: str
    # Literal limita las opciones a 'Cliente' o 'Cuidador'
    tipo: Literal["Cliente", "Cuidador"] 

# Modelo Pydantic para los datos que la API retornará (respuesta exitosa)
class UserOut(BaseModel):
    id: int # Asumiremos un ID (clave primaria) de la DB
    nombre: str
    email: EmailStr
    tipo: str
    
    # Configuración opcional
    class Config:
        # Permite que Pydantic lea atributos de clases que no son diccionarios (como tus clases de dominio)
        from_attributes = True

# Esquema para la solicitud de Login
class TokenRequest(BaseModel):
    # Usaremos EmailStr para validar el formato del email
    email: EmailStr
    contrasena: str

# Nuevo: Esquema para la respuesta del Login (el JWT)
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer" # Es estándar que sea un token de tipo 'bearer'