from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

#Imporatciones locales 
from petcare.core.database import get_db
from petcare.schemas.resena_schemas import ReviewCreate, ReviewOut
from petcare.core.resena_services import (
    create_review,
    get_reviews_by_cuidador,
    get_cuidador_puntaje
)

review_router = APIRouter(prefix="/reviews", tags=["Reseñas"])


@review_router.post("/", response_model=ReviewOut, status_code=201)
def create_review_endpoint(
    payload: ReviewCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva reseña (review) en la base de datos.
    """
    return create_review(db=db, data=payload)


@review_router.get("/cuidador/{cuidador_id}", response_model=list[ReviewOut])
def list_reviews(
    cuidador_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las reseñas para un cuidador específico.
    """
    return get_reviews_by_cuidador(db, cuidador_id)


@review_router.get("/cuidador/{cuidador_id}/rating")
def promedio_rating(
    cuidador_id: int,
    db: Session = Depends(get_db)
):
    """
    Calcula y devuelve el puntaje de rating promedio de un cuidador.
    """
    return {
        "cuidador_id": cuidador_id,
        "promedio_rating": get_cuidador_puntaje(db, cuidador_id)
    }
