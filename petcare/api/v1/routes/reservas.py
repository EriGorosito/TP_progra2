from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import date

from petcare.schemas.reserva_schema import ReservaCreate, ReservaOut
from petcare.core.reserva_services import create_reserva, buscar_cuidadores_disponibles
from petcare.core.security import get_current_user
from petcare.domain.usuario import Usuario

reserva_router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"]
)

@reserva_router.post("/", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
async def nueva_reserva(reserva_data: ReservaCreate, current_user: Usuario = Depends(get_current_user)):
    if current_user.user_type != "Cliente":
        raise HTTPException(status_code=403, detail="Solo Clientes pueden crear reservas.")
    
    # Lógica: buscar cuidador
    cuidador = reserva_data.cuidador  # simplificado, puede usar buscar_cuidador_disponible #cuidador = buscar_cuidador_disponible(tipo_mascota,fecha_inicio,fecha_fin,ubicacion,mascotas_reserva)
    reserva = create_reserva(
        cliente=current_user,
        cuidador=cuidador,
        mascotas=reserva_data.mascotas,
        fecha_inicio=reserva_data.fecha_inicio,
        fecha_fin=reserva_data.fecha_fin
    )
    return reserva
