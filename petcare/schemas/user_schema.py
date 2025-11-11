#schemas/user_schemas.py
from pydantic import BaseModel, EmailStr
from typing import Literal

# Modelo Pydantic para los datos que el usuario envía al registrarse
class UserCreate(BaseModel):
    # Usamos EmailStr para una validación de formato automática
    email: EmailStr
    nombre: str
    contrasena: str
    # Literal limita las opciones a 'Cliente' o 'Cuidador'
    tipo: Literal["Cliente", "Cuidador", "cliente", "cuidador"]
    direccion: str 

# Modelo Pydantic para los datos que la API retornará (respuesta exitosa)
class UserOut(BaseModel):
    id: int 
    nombre: str
    email: EmailStr
    tipo: str
    direccion: str
    lat: float
    lon: float
    map_url: str 
    
    # Configuración opcional
    class Config:
        # Permite que Pydantic lea atributos de clases que no son diccionarios (como tus clases de dominio)
        from_attributes = True

# Esquema para la solicitud de Login
class TokenRequest(BaseModel):
    # Usaremos EmailStr para validar el formato del email
    email: EmailStr
    contrasena: str

# Esquema para la respuesta del Login (el JWT)
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer" # Es estándar que sea un token de tipo 'bearer'

class UserUpdateDireccion(BaseModel):
    direccion: str