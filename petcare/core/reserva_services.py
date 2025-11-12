from datetime import date
from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException

#Importaciones locales

from petcare.core.cuidador_services import cuidador_disponible
from petcare.domain.especie import Especie
from petcare.domain.observer import event_manager
from petcare.infraestructura.models.usuario_model import Cuidador
from petcare.infraestructura.models.mascota_model import Mascota
from petcare.infraestructura.models.resena_model import Resena
from petcare.infraestructura.models.reserva_model import Reserva, reserva_mascota
from petcare.infraestructura.models.usuario_model import Usuario


def create_reserva(
    db: Session,
    cliente: Usuario,
    mascotas: List[Mascota],
    cuidador: Cuidador,
    fecha_inicio: date,
    fecha_fin: date,
    event_manager=None
) -> Reserva:
    """
    Crea una nueva reserva después de verificar la disponibilidad del cuidador.
    """
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
    # "añades" los objetos Mascota a la lista.
    #  SQLAlchemy sabe que debe crear las filas en la tabla 'reserva_mascota'.
    nueva_reserva.mascotas.extend(mascotas)
    
    # 3. Añades SOLO la reserva a la sesión.
    db.add(nueva_reserva)

    try:
        # 4. UN SOLO COMMIT
        #    Esto guarda la reserva Y las asociaciones en la tabla puente.
        #    Si falla, NADA se guarda. Es 100% atómico.
        db.commit()
        db.refresh(nueva_reserva) # Para obtener el ID

        # 5. Notificar (con el arreglo de IDs que arregla el error ObjectDeletedError)
        if event_manager:
            data_payload = {
                "cliente_id": cliente.id,
                "cuidador_id": cuidador.id,
                "reserva_id": nueva_reserva.id,
                "fecha_inicio_str": nueva_reserva.fecha_inicio.isoformat(),
                "estado": nueva_reserva.estado
            }
            event_manager.notify("reserva_creada", data_payload)

        return nueva_reserva

    except Exception as e:
        # Si algo falla (la reserva O las mascotas), revertimos TODO.
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear la reserva: {e}"
        )


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
    # El cuidador debe ser el dueño de la reserva para modificarla
    if reserva.cuidador_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="No autorizado para modificar esta reserva."
        )

    # Prevenir modificaciones a estados finales o ya modificados
    if reserva.estado in ("rechazada", "completada"):
        raise HTTPException(
            status_code=400,
            detail=f"No se puede modificar una reserva {reserva.estado}."
        )

    estados_validos = {"aceptada", "rechazada", "Aceptada", "Rechazada"}
    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado '{nuevo_estado}' no permitido. Solo se puede aceptar o rechazar."
        )

    reserva.estado = nuevo_estado
    db.commit()
    db.refresh(reserva)

    return reserva

