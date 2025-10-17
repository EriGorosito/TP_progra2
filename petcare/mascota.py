from typing import Optional


class Mascota:
    def __init__(self, nombre: str, tipo: str, edad: int, peso: float, caracteristicas: Optional[str] = None):
        self.nombre = nombre
        self.tipo = tipo
        self.edad = edad
        self.peso = peso
        self.caracteristicas = caracteristicas

    def mostrar_info(self):
        pass