from petcare.domain.models.resena_model import Resena
from petcare.tasks.update_reserva import actualizar_reservas_finalizadas
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from petcare.domain.models.reserva_model import Reserva
from petcare.schemas.resena_schemas import ReviewCreate


def create_review(db: Session, data: ReviewCreate):

    actualizar_reservas_finalizadas(db)
    reserva = db.query(Reserva).filter(Reserva.id == data.reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.estado != "finalizada":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden dejar reseñas de reservas finalizadas"
        )

    if reserva.resena:
        raise HTTPException(
            status_code=400,
            detail="La reserva ya tiene reseña"
        )

    db_resena = Resena(
        puntaje=data.puntaje,
        comentario=data.comentario,
        cliente_id=reserva.cliente_id,
        cuidador_id=reserva.cuidador_id,
        reserva_id=reserva.id,
    )

    db.add(db_resena)
    db.commit()
    db.refresh(db_resena)

    return db_resena


def get_reviews_by_cuidador(db: Session, cuidador_id: int):
    return db.query(Resena).filter(Resena.cuidador_id == cuidador_id).all()


def get_cuidador_puntaje(db: Session, cuidador_id: int):
    resenas = get_reviews_by_cuidador(db, cuidador_id)
    if not resenas:
        return 0
    return sum(r.puntaje for r in resenas) / len(resenas)
