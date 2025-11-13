from datetime import date
from typing import List

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

#Imporataciones locales
from petcare.core.database import get_db
from petcare.core.reserva_services import create_reserva, event_manager
from petcare.schemas.reserva_schema import ReservaCreate, ReservaOut
from petcare.core.security import get_current_user
from petcare.infraestructura.models.usuario_model import Usuario
from petcare.infraestructura.models.reserva_model import Reserva
from petcare.infraestructura.models.mascota_model import Mascota
from petcare.core.reserva_services import actualizar_estado_reserva
from petcare.core.reserva_services import finalizar_reserva


reserva_router = APIRouter(prefix="/reservas", tags=["Reservas"])


@reserva_router.post(
    "/", 
    response_model=ReservaOut, 
    status_code=status.HTTP_201_CREATED
)
async def nueva_reserva(
    reserva_data: ReservaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva reserva. Solo permitido para usuarios 'Cliente'.
    """
    if current_user.tipo.lower() != "cliente":
        raise HTTPException(
            status_code=403, 
            detail="Solo Clientes pueden crear reservas."
        )

    # Verificar que el cuidador existe
    cuidador = db.query(Usuario).filter(Usuario.id == reserva_data.cuidador_id).first()
    if not cuidador:
        raise HTTPException(status_code=404, detail="Cuidador no encontrado.")

    #Verificar que las mascotas existen
    mascotas = db.query(Mascota).filter(Mascota.id.in_(reserva_data.mascotas_ids)).all()
    if not mascotas:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron mascotas con esos IDs."
        )

    # Crear la reserva
    reserva = create_reserva(
        db=db,
        cliente=current_user,
        cuidador=cuidador,
        mascotas=mascotas,
        fecha_inicio=reserva_data.fecha_inicio,
        fecha_fin=reserva_data.fecha_fin,
        event_manager=event_manager
    )

    return reserva


@reserva_router.put("/{reserva_id}/aceptar")
async def aceptar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Permite al cuidador aceptar una reserva pendiente.
    """
    if current_user.tipo.lower() != "cuidador":
        raise HTTPException(
            status_code=403, 
            detail="Solo cuidadores pueden aceptar reservas."
        )

    #Buscar la reserva en la base de datos
    reserva = db.query(Reserva).filter_by(id=reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reserva.cuidador_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="No puedes aceptar reservas de otro cuidador."
        )


    reserva.estado = "aceptada"
    db.commit()
    db.refresh(reserva)

    event_manager.notify("reserva_aceptada", {"reserva": reserva})
    return {"mensaje": "Reserva confirmada con éxito", "reserva": reserva}


@reserva_router.get("/mias", response_model=List[ReservaOut])
def obtener_reservas_actuales(
    estado: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve las reservas del usuario actual (cliente o cuidador), 
    filtradas opcionalmente por estado y rango de fechas.
    """
    query = db.query(Reserva)

    if current_user.tipo.lower() == "cliente":
        query = query.filter(Reserva.cliente_id == current_user.id)
    else:
        query = query.filter(Reserva.cuidador_id == current_user.id)

    if estado:
        query = query.filter(Reserva.estado == estado)
    # Se utiliza el operador de comparación implícita para chequear si ambas existen
    if desde and hasta:
        query = query.filter(Reserva.fecha_inicio >= desde, Reserva.fecha_fin <= hasta)

    return query.all()


@reserva_router.patch("/{reserva_id}/estado", response_model=ReservaOut)
def actualizar_estado(
    reserva_id: int,
    estado_reserva: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza el estado de una reserva (ej: 'cancelada', 'aceptada').
    """
    return actualizar_estado_reserva(
        db=db,
        reserva_id=reserva_id,
        nuevo_estado=estado_reserva,
        current_user=current_user
    )


@reserva_router.put(
    "/reservas/{reserva_id}/finalizar", 
    response_model=ReservaOut, 
    status_code=status.HTTP_200_OK,
    summary="Finalizar una reserva manualmente"
)
def finalizar_reserva_endpoint(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Permite al cuidador marcar una reserva como finalizada.
    Solo permitido:
    - Si el usuario es el cuidador de la reserva.
    - Si la reserva estaba 'aceptada'.
    """
    reserva_actualizada = finalizar_reserva(
        db=db,
        reserva_id=reserva_id,
        current_user=current_user
    )
    return reserva_actualizada