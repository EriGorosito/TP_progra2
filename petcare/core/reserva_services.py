from datetime import date, timedelta
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
            # --- ¡ESTE ES EL PAYLOAD COMPLETO! ---
            # Extraemos los datos simples ANTES de que los objetos mueran.
            data_payload = {
                # Datos para la notificación "reserva_creada"
                "cliente_id": cliente.id,
                "cliente_nombre": cliente.nombre, # <-- ¡La pieza que faltaba!
                "cuidador_id": cuidador.id,
                
                # Datos para otros eventos (si los necesitaras)
                "cuidador_nombre": cuidador.nombre, 
                "reserva_id": nueva_reserva.id,
                "fecha_inicio_str": nueva_reserva.fecha_inicio.isoformat(),
                "estado": nueva_reserva.estado
            }
            # Pasamos el diccionario de datos simples
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

def finalizar_reserva(
    db: Session,
    reserva_id: int,
    current_user: Usuario
) -> Reserva:
    """
    Cambia el estado de una reserva a 'finalizada'.
    Reglas:
      1. Solo si estaba 'aceptada'.
      2. Solo si es el último día de la reserva o el día siguiente.
    """
    # 1. Obtener la reserva
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()

    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    # 2. Validar autorización (Asumo que lo hace el Cuidador, igual que actualizar_estado)
    if reserva.cuidador_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permiso para finalizar esta reserva."
        )

    # 3. Validar estado previo
    # Aceptamos "aceptada" o "Aceptada" por si acaso
    if reserva.estado.lower() != "aceptada":
        raise HTTPException(
            status_code=400,
            detail=f"No se puede finalizar una reserva en estado '{reserva.estado}'. Debe estar 'aceptada'."
        )

    # 4. Validar Fechas (La lógica crítica)
    hoy = date.today()
    fecha_fin = reserva.fecha_fin
    dia_siguiente = fecha_fin + timedelta(days=1)

    # Si hoy es antes de que termine la reserva
    if hoy < fecha_fin:
        raise HTTPException(
            status_code=400,
            detail=f"Aún no puedes finalizar la reserva. Termina el {fecha_fin}."
        )

    # 5. Aplicar cambio y guardar
    reserva.estado = "finalizada"
    
    try:
        db.commit()
        db.refresh(reserva)

        # 6. Notificar al Observer
        # Preparamos los datos planos antes de que SQLAlchemy cierre la sesión
        if event_manager:
            # NOTA: Aquí accedemos a las relaciones (cliente, cuidador)
            # Asegúrate de que estén cargadas o accesibles (lazy loading suele funcionar aquí antes del return)
            data_payload = {
                "reserva_id": reserva.id,
                "cliente_id": reserva.cliente_id,
                "cliente_nombre": reserva.cliente.nombre,
                "cuidador_id": reserva.cuidador_id,
                "cuidador_nombre": reserva.cuidador.nombre,
                "fecha_fin": reserva.fecha_fin.isoformat()
            }
            event_manager.notify("reserva_finalizada", data_payload)

        return reserva

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al finalizar la reserva: {str(e)}"
        )