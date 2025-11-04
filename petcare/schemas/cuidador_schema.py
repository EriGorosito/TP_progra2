#petcate/schemas/cuidador_schema.py
from pydantic import BaseModel, field_validator
from typing import List, Dict, Optional
from datetime import date
from petcare.domain.especie import Especie

class CuidadorCreate(BaseModel):
    descripcion: Optional[str] = None
    servicios: List[Especie]
    tarifas: Optional[Dict[str, float]] = None
    dias_no_disponibles: Optional[List[date]] = None

# @field_validator("servicios", mode="before")
# def validar_servicios(cls, v):
#     # Si vienen como strings desde el JSON, los convierte al Enum
#     if isinstance(v, list):
#         return [Especie(s) if not isinstance(s, Especie) else s for s in v]
#     raise ValueError("El campo servicios debe ser una lista")

class Config:
    use_enum_values = True  # <- convierte Enum a su valor (string) al exportar

class CuidadorOut(BaseModel):
    id: int

    class Config:
        orm_mode = True