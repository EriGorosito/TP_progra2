from typing import Optional
from dataclasses import dataclass

@dataclass
class Mascota:
    id: int
    nombre: str
    especie: str
    raza: str
    edad: int
    peso: float

    # Importante: El ID del usuario "Cliente" que es el dueño
    owner_id: int
    
    # Características especiales (medicación, alergias, etc.)
    caracteristicas_especiales: str | None = None
    
    

    def mostrar_info(self):
        pass