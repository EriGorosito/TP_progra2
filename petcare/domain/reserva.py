#petcare/domain/reserva.py
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

    def crear(self, event_manager=None):
        if event_manager:
            event_manager.notify("reserva_creada", {
                "cliente": self.cliente,
                "cuidador": self.cuidador,
                "reserva": self
            })


    def confirmar(self, event_manager=None):
        self.estado = "confirmada"
        if event_manager:
            event_manager.notify("reserva_confirmada", {
                "cliente": self.cliente,
                "cuidador": self.cuidador,
                "reserva": self
            })


    def rechazar(self, event_manager=None):
        self.estado = "rechazada"
        if event_manager:
            event_manager.notify("reserva_rechazada", {
                "cliente": self.cliente,
                "cuidador": self.cuidador,
                "reserva": self
            })


    def calcular_costo(self) -> float:
        """Suma el costo diario por cada especie de mascota multiplicado por los días"""
        dias = (self.fecha_fin - self.fecha_inicio).days + 1
        total = 0
        for m in self.mascotas:
            precio = self.cuidador.tarifas.get(m.especie, 0)
            total += precio * dias
        return total
    
    def __str__(self):
        return f"Reserva #{self.id} - {self.estado} ({self.fecha_inicio} → {self.fecha_fin})"
