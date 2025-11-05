# petcare/core/reserva_services.py
from datetime import date
from typing import List
from petcare.domain.especie import Especie
from petcare.domain.reserva import Reserva
from petcare.domain.usuario import Cliente, Cuidador
from petcare.domain.mascota import Mascota
from petcare.domain.observer import event_manager
from petcare.core.map_services import distancia_geodesica


# Mock de datos en memoria
MOCK_RESERVAS: List[Reserva] = []
next_reserva_id = 1

def buscar_cuidadores_disponibles(
    cuidadores: List[Cuidador],
    mascotas: List[Mascota],
    fecha_inicio: date,
    fecha_fin: date,
    ubicacion_cliente: tuple
) -> List[Cuidador]:
    """
    Filtra los cuidadores disponibles y los ordena por distancia al cliente.
    """
    especie_requeridas = {m.especie for m in mascotas}

    cuidadores_filtrados = []
    for c in cuidadores:
        # Filtrar por especie
        if not especie_requeridas.issubset(set(c.servicios)):
            continue

        # Filtrar por disponibilidad
        if not c.esta_disponible(fecha_inicio, fecha_fin):
            continue

        # Calcular distancia al cliente
        distancia = distancia_geodesica(ubicacion_cliente, c.ubicacion)

        cuidadores_filtrados.append((c, distancia))

    # Ordenar por distancia
    cuidadores_filtrados.sort(key=lambda x: x[1])
    return [c for c, _ in cuidadores_filtrados]


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


# def buscar_cuidadores_disponibles(
#     tipo_mascota: Especie,
#     fecha_inicio: date,
#     fecha_fin: date,
#     cuidadores: List[Cuidador]
# ) -> List[Cuidador]:
#     """
#     Retorna solo los cuidadores que pueden cuidar la especie y están libres en todo el rango de fechas
#     """
#     return [
#         c for c in cuidadores
#         if tipo_mascota in c.servicios and c.esta_disponible(fecha_inicio, fecha_fin)
#     ]