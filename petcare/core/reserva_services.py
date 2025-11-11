# petcare/core/reserva_services.py
from datetime import date
from typing import List
from petcare.domain.especie import Especie
from petcare.domain.reserva import Reserva
from petcare.domain.models.cuidador_model import Cuidador
from petcare.domain.models.mascota_model import Mascota
from petcare.domain.observer import event_manager
from petcare.core.cuidador_services import cuidador_disponible
from sqlalchemy.orm import Session
from petcare.domain.models.resena_model import Resena
from petcare.domain.models.reserva_model import Reserva, reserva_mascota
from petcare.domain.models.usuario_model import Usuario
from fastapi import HTTPException


# def buscar_cuidadores_disponibles(
#     cuidadores: List[Cuidador],
#     mascotas: List[Mascota],
#     fecha_inicio: date,
#     fecha_fin: date,
#     ubicacion_cliente: tuple
# ) -> List[Cuidador]:
#     """
#     Filtra los cuidadores disponibles y los ordena por distancia al cliente.
#     """
#     especie_requeridas = {m.especie for m in mascotas}

#     cuidadores_filtrados = []
#     for c in cuidadores:
#         # Filtrar por especie
#         if not especie_requeridas.issubset(set(c.servicios)):
#             continue

#         # Filtrar por disponibilidad
#         if not c.esta_disponible(fecha_inicio, fecha_fin):
#             continue

#         # Calcular distancia al cliente
#         distancia = distancia_geodesica(ubicacion_cliente, c.ubicacion)

#         cuidadores_filtrados.append((c, distancia))

#     # Ordenar por distancia
#     cuidadores_filtrados.sort(key=lambda x: x[1])
#     return [c for c, _ in cuidadores_filtrados]


def create_reserva(
    db: Session,
    cliente: Usuario,
    mascotas: List[Mascota],
    cuidador: Cuidador,
    fecha_inicio: date,
    fecha_fin: date,
    event_manager=None
) -> Reserva:

    if not cuidador_disponible(db, cuidador.id, fecha_inicio, fecha_fin):
        raise HTTPException(
            status_code=400,
            detail="El cuidador no está disponible en esas fechas."
        )
   

    nueva_reserva = Reserva(
        cliente_id=cliente.id,
        cuidador_id=cuidador.id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="pendiente"
    )

    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)

    # Asignar mascotas
    for mascota in mascotas:
        db.execute(
            reserva_mascota.insert().values(
                reserva_id=nueva_reserva.id,
                mascota_id=mascota.id
            )
        )
    db.commit()

    if event_manager:
        event_manager.notify("reserva_creada", {
            "cliente": cliente,
            "cuidador": cuidador,
            "reserva": nueva_reserva
        })

    return nueva_reserva

def actualizar_estado_reserva(
    db: Session,
    reserva_id: int,
    nuevo_estado: str,
    current_user: Usuario
) -> Reserva:
    """Lógica de negocio para cambiar el estado de una reserva."""
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()


    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")


    if reserva.cuidador_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para modificar esta reserva.")


    if reserva.estado in ("rechazada", "completada"):
        raise HTTPException(
            status_code=400,
            detail=f"No se puede modificar una reserva {reserva.estado}."
        )


    reserva.estado = nuevo_estado
    db.commit()
    db.refresh(reserva)


    return reserva


# def get_reservas_by_cliente(cliente: Cliente) -> List[Reserva]:
#     return [r for r in MOCK_RESERVAS if r.cliente.id == cliente.id]


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