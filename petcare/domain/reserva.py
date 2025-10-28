from datetime import date
from typing import List
from petcare.domain.usuario import Cliente, Cuidador
from petcare.domain.mascota import Mascota

class Reserva:
    def __init__(self, id: int, cliente: Cliente, cuidador: Cuidador, mascotas: List[Mascota], fecha_inicio: date, fecha_fin: date, estado: str='pendiente'):
        self.id = id
        self.cliente = cliente
        self.cuidador = cuidador
        self.mascotas = mascotas  # lista de mascotas
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado

    def confirmar(self):
        self.estado = "confirmada"

    def rechazar(self):
        self.estado = "rechazada"

    def calcular_costo(self) -> float:
        """Suma el costo diario por cada especie de mascota multiplicado por los días"""
        dias = (self.fecha_fin - self.fecha_inicio).days + 1
        total = 0
        for m in self.mascotas:
            precio = self.cuidador.tarifas.get(m.especie, 0)
            total += precio * dias
        return total


