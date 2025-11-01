from datetime import date
from typing import List
from petcare.domain.reserva import Reserva
from petcare.domain.usuario import Cliente, Cuidador
from petcare.domain.mascota import Mascota
from petcare.domain.observer import EventManager, NotificationObserver

# Mock de datos en memoria
MOCK_RESERVAS: List[Reserva] = []
next_reserva_id = 1

# Inicializamos el sistema de eventos
event_manager = EventManager()
noti_observer = NotificationObserver()
event_manager.subscribe("reserva_creada", noti_observer)
event_manager.subscribe("reserva_confirmada", noti_observer)
event_manager.subscribe("reserva_rechazada", noti_observer)

def create_reserva(
    cliente: Cliente,
    mascotas: List[Mascota],
    cuidador: Cuidador,
    fecha_inicio: date,
    fecha_fin: date,
    event_manager=None
) -> Reserva:
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

    if event_manager:
        event_manager.notify("reserva_creada", {
            "cliente": cliente,
            "cuidador": cuidador,
            "reserva": new_reserva
        })

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
    return [
        c for c in cuidadores
        if tipo_mascota in c.servicios and c.esta_disponible(fecha_inicio, fecha_fin)
    ]
