# from fastapi import APIRouter, Depends, HTTPException, status
# from typing import List
# from datetime import date

# from petcare.schemas.reserva_schema import ReservaCreate, ReservaOut
# from petcare.core.reserva_services import create_reserva, buscar_cuidadores_disponibles
# from petcare.core.security import get_current_user
# from petcare.domain.usuario import Usuario

# reserva_router = APIRouter(
#     prefix="/reservas",
#     tags=["Reservas"]
# )

# @reserva_router.post("/", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
# async def nueva_reserva(reserva_data: ReservaCreate, current_user: Usuario = Depends(get_current_user)):
#     if current_user.user_type != "Cliente":
#         raise HTTPException(status_code=403, detail="Solo Clientes pueden crear reservas.")
    
#     # Lógica: buscar cuidador
#     cuidador = reserva_data.cuidador  # simplificado, puede usar buscar_cuidador_disponible #cuidador = buscar_cuidador_disponible(tipo_mascota,fecha_inicio,fecha_fin,ubicacion,mascotas_reserva)
#     reserva = create_reserva(
#         cliente=current_user,
#         cuidador=cuidador,
#         mascotas=reserva_data.mascotas,
#         fecha_inicio=reserva_data.fecha_inicio,
#         fecha_fin=reserva_data.fecha_fin
#     )
#     return reserva
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import date

from petcare.schemas.reserva_schema import ReservaCreate, ReservaOut
from petcare.core.reserva_services import create_reserva, buscar_cuidadores_disponibles #, noti_observer
from petcare.core.security import get_current_user
from petcare.domain.usuario import Usuario
from petcare.core.reserva_services import create_reserva, event_manager

reserva_router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"]
)

@reserva_router.post("/", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
async def nueva_reserva(reserva_data: ReservaCreate, current_user: Usuario = Depends(get_current_user)):
    if current_user.user_type != "Cliente":
        raise HTTPException(status_code=403, detail="Solo Clientes pueden crear reservas.")
    
    # Lógica simplificada: obtener cuidador desde el request
    cuidador = reserva_data.cuidador

    # Crear reserva (esto dispara la notificación automáticamente)
    reserva = create_reserva(
        cliente=current_user,
        cuidador=cuidador,
        mascotas=reserva_data.mascotas,
        fecha_inicio=reserva_data.fecha_inicio,
        fecha_fin=reserva_data.fecha_fin
    )
    reserva = create_reserva(
        cliente=current_user,
        cuidador=cuidador,
        mascotas=reserva_data.mascotas,
        fecha_inicio=reserva_data.fecha_inicio,
        fecha_fin=reserva_data.fecha_fin,
        event_manager=event_manager
    )

    # OPCIONAL: devolver también la última notificación generada
    ultima_noti = noti_observer.notificaciones[-1] if noti_observer.notificaciones else None

    return {
        "reserva": reserva,
        "notificacion": ultima_noti
    }

from petcare.core.reserva_services import MOCK_RESERVAS

#para que el cuidador acepte y rechaze la reserva
@reserva_router.put("/{reserva_id}/aceptar", status_code=status.HTTP_200_OK)
async def aceptar_reserva(reserva_id: int, current_user: Usuario = Depends(get_current_user)):
    # Solo cuidadores pueden aceptar reservas
    if current_user.user_type != "Cuidador":
        raise HTTPException(status_code=403, detail="Solo cuidadores pueden aceptar reservas.")

    # Buscar reserva
    reserva = next((r for r in MOCK_RESERVAS if r.id == reserva_id), None)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    # Verificar que le pertenece al cuidador actual
    if reserva.cuidador.id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes aceptar reservas de otro cuidador.")

    # Confirmar y marcar no disponibles los días
    current_user.aceptar_reserva(reserva, event_manager)

    return {"mensaje": "Reserva confirmada con éxito", "reserva": str(reserva)}


@reserva_router.put("/{reserva_id}/rechazar", status_code=status.HTTP_200_OK)
async def rechazar_reserva(reserva_id: int, current_user: Usuario = Depends(get_current_user)):
    # Solo cuidadores pueden rechazar reservas
    if current_user.user_type != "Cuidador":
        raise HTTPException(status_code=403, detail="Solo cuidadores pueden rechazar reservas.")

    reserva = next((r for r in MOCK_RESERVAS if r.id == reserva_id), None)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reserva.cuidador.id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes rechazar reservas de otro cuidador.")

    current_user.rechazar_reserva(reserva, event_manager)

    return {"mensaje": "Reserva rechazada", "reserva": str(reserva)}
