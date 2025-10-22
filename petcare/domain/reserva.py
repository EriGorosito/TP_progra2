from datetime import date
from petcare.domain.mascota import Mascota
from petcare.domain.usuario import Cliente, Cuidador


class Reserva:
    def __init__(self, cliente: Cliente, cuidador: Cuidador, mascota: Mascota, fecha_inicio: date, fecha_fin: date):
        self.cliente = cliente
        self.cuidador = cuidador
        self.mascota = mascota
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = "Pendiente"

    def confirmar(self):
        pass

    def rechazar(self):
        pass

    def calcular_costo(self):
        pass
