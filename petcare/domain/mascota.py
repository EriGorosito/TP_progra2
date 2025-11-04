from typing import Optional
from dataclasses import dataclass

from petcare.domain.especie import Especie

@dataclass
class Mascota:
    id: int
    nombre: str
    especie: Especie
    raza: str
    edad: int
    peso: float

    # Importante: El ID del usuario "Cliente" que es el dueño
    owner_id: int
    
    # Características especiales (medicación, alergias, etc.)
    caracteristicas_especiales: str | None = None
    
    

    def mostrar_info(self):
        pass