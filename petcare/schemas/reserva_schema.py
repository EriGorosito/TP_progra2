from datetime import date
from typing import List

from pydantic import BaseModel

#Importaciones locales
from petcare.schemas.pet_schema import PetOut
from petcare.schemas.user_schema import UserOut


class ReservaCreate(BaseModel):
    mascotas_ids: List[int]
    cuidador_id: int
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