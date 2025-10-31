from pydantic import BaseModel
from datetime import date
from typing import List
from petcare.schemas.pet_schema import PetOut
from petcare.schemas.user_schema import UserOut

class ReservaCreate(BaseModel):
    mascotas: List[PetOut]
    cuidador: UserOut
    fecha_inicio: date
    fecha_fin: date

class ReservaOut(BaseModel):
    id: int
    cliente: UserOut
    cuidador: UserOut
    mascotas: List[PetOut]
    fecha_inicio: date
    fecha_fin: date
    estado: str