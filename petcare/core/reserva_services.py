from datetime import date
from typing import List
from petcare.domain.reserva import Reserva
from petcare.domain.usuario import Cliente, Cuidador
from petcare.domain.mascota import Mascota
from petcare.domain.especie import Especie

MOCK_RESERVAS: List[Reserva] = []
next_reserva_id = 1

def buscar_cuidadores_disponibles(
    tipo_mascota: Especie,
    fecha_inicio: date,
    fecha_fin: date,
    cuidadores: List[Cuidador],
    ubicacion: str | None = None
) -> List[Cuidador]:
    """
    Retorna solo los cuidadores que pueden cuidar la especie y están libres en todo el rango de fechas
    y opcionalmente en la ubicación indicada.
    """
    disponibles = []
    for c in cuidadores:
        if tipo_mascota in c.servicios and c.esta_disponible(fecha_inicio, fecha_fin):
            if ubicacion is None or c.ubicacion.lower() == ubicacion.lower():
                disponibles.append(c)
    return disponibles


def create_reserva(cliente: Cliente, mascotas: List[Mascota],
                   cuidadores: List[Cuidador], fecha_inicio: date, fecha_fin: date, ubicacion: str) -> Reserva:
    """
    Busca un cuidador adecuado y crea una nueva reserva.
    """
    global next_reserva_id

    if not mascotas:
        raise ValueError("Debe incluir al menos una mascota en la reserva.")

    tipo_mascota = mascotas[0].especie

    posibles_cuidadores = buscar_cuidadores_disponibles(tipo_mascota, fecha_inicio, fecha_fin, cuidadores, ubicacion)

    if not posibles_cuidadores:
        raise ValueError("No hay cuidadores disponibles para esa especie, fecha o ubicación.")

    cuidador = posibles_cuidadores[0]  # se puede mejorar con lógica de ranking más adelante

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

