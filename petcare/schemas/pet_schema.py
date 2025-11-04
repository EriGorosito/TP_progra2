from pydantic import BaseModel
from typing import Optional
from petcare.domain.especie import Especie

# Esquema base con campos comunes
class PetBase(BaseModel):
    nombre: str
    especie: Especie
    raza: Optional[str] = None
    edad: int
    peso: float
    caracteristicas_especiales: Optional[str] = None

# Esquema para la creación (lo que envía el usuario)
class PetCreate(PetBase):
    pass # Por ahora es igual a PetBase

# Esquema para la respuesta (lo que devuelve la API)
class PetOut(PetBase):
    id: int
    nombre: str
    owner_id: int # Mostramos el ID del dueño

    class Config:
        from_attributes = True