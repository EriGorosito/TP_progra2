#petcate/schemas/cuidador_schema.py
from datetime import date
from typing import List, Dict, Optional

from pydantic import BaseModel

from petcare.domain.especie import Especie

class CuidadorCreate(BaseModel):
    descripcion: Optional[str] = None
    servicios: List[Especie]
    tarifas: Optional[Dict[str, float]] = None
    dias_no_disponibles: Optional[List[date]] = None

    class Config:
        """
        Configuración interna de Pydantic para esta clase.
        """
        use_enum_values = True  # convierte Enum a su valor (string) al exportar


class CuidadorOut(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True