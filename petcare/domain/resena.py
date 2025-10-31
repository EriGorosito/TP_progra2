# resena.py
from typing import Optional

class Resena:
    def __init__(self, id: int, cliente, cuidador, puntaje: int, comentario: Optional[str] = None):
        self.id = id
        self.cliente = cliente
        self.cuidador = cuidador
        self.puntaje = puntaje
        self.comentario = comentario or ""

    def mostrar(self):
        return f"{self.cliente.nombre} calificó a {self.cuidador.nombre} con {self.puntaje}/10"
