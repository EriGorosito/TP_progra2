from sqlalchemy.orm import Session
from fastapi import HTTPException, status

#Importaciones locales 
from petcare.infraestructura.models.resena_model import Resena
from petcare.tasks.update_reserva import actualizar_reservas_finalizadas
from petcare.infraestructura.models.reserva_model import Reserva
from petcare.schemas.resena_schemas import ReviewCreate
from petcare.infraestructura.models.usuario_model import Usuario as UsuarioModel


def create_review(db: Session, data: ReviewCreate, current_user: UsuarioModel):
    """
    Crea una nueva reseña después de verificar que la reserva asociada 
    esté finalizada y no tenga una reseña previa.
    """
    # 1. Verificar que el usuario sea CLIENTE
    if current_user.tipo != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden dejar reseñas."
        )
    
    # 2. Actualizar reservas finalizadas
    actualizar_reservas_finalizadas(db)

     # 3. Buscar la reserva
    reserva = db.query(Reserva).filter(Reserva.id == data.reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    # 4. Verificar que el cliente sea el dueño de la reserva
    if reserva.cliente_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes reseñar tus propias reservas."
        )
    
    # 5. Verificar estado finalizado
    if reserva.estado != "finalizada":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden dejar reseñas de reservas finalizadas"
        )

    # 6. Verificar que no exista reseña previa
    if reserva.resena:
        raise HTTPException(
            status_code=400,
            detail="La reserva ya tiene reseña"
        )

    # 7. Crear reseña
    db_resena = Resena(
        puntaje=data.puntaje,
        comentario=data.comentario,
        cliente_id=current_user.id,
        cuidador_id=reserva.cuidador_id,
        reserva_id=reserva.id,
    )

    db.add(db_resena)
    db.commit()
    db.refresh(db_resena)

    return db_resena


def get_reviews_by_cuidador(db: Session, cuidador_id: int):
    """
    Obtiene todas las reseñas para un cuidador específico.
    """
    return db.query(Resena).filter(Resena.cuidador_id == cuidador_id).all()


def get_cuidador_puntaje(db: Session, cuidador_id: int):
    """
    Calcula el puntaje (rating) promedio del cuidador.
    Devuelve 0 si no hay reseñas.
    """
    resenas = get_reviews_by_cuidador(db, cuidador_id)
    if not resenas:
        return 0
    
    return sum(r.puntaje for r in resenas) / len(resenas)


