from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreate(BaseModel):
    puntaje: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None
    reserva_id: int


class ReviewOut(BaseModel):
    id: int
    puntaje: int
    comentario: Optional[str]
    cliente_id: int
    cuidador_id: int
    reserva_id: int

    class Config:
        orm_mode = True
