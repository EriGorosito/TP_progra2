from datetime import date
from typing import List
from petcare.domain.reserva import Reserva
from petcare.domain.usuario import Cliente, Cuidador
from petcare.domain.mascota import Mascota

MOCK_RESERVAS: List[Reserva] = []
next_reserva_id = 1

def create_reserva(cliente: Cliente, mascotas: List[Mascota],
                   cuidador: Cuidador, fecha_inicio: date, fecha_fin: date) -> Reserva:
    """
    Crea una nueva reserva para varias mascotas y un cuidador, si está disponible.
    """
    global next_reserva_id

    if not cuidador.esta_disponible(fecha_inicio, fecha_fin):
        raise ValueError("El cuidador no está disponible en esas fechas.")

    new_reserva = Reserva(
        id=next_reserva_id,
        cliente=cliente,
        cuidador=cuidador,
        mascotas=mascotas,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="pendiente"
    )

    MOCK_RESERVAS.append(new_reserva)
    next_reserva_id += 1
    return new_reserva

def get_reservas_by_cliente(cliente: Cliente) -> List[Reserva]:
    return [r for r in MOCK_RESERVAS if r.cliente.id == cliente.id]


def buscar_cuidadores_disponibles(
    tipo_mascota: str,
    fecha_inicio: date,
    fecha_fin: date,
    cuidadores: List[Cuidador]
) -> List[Cuidador]:
    """
    Retorna solo los cuidadores que pueden cuidar la especie y están libres en todo el rango de fechas
    """
    disponibles = []
    for c in cuidadores:
        if tipo_mascota in c.servicios and c.esta_disponible(fecha_inicio, fecha_fin):
            disponibles.append(c)
    return disponibles
