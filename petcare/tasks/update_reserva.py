from datetime import date
from sqlalchemy.orm import Session
from petcare.core.database import SessionLocal
from petcare.infraestructura.models.reserva_model import Reserva


def _actualizar_reservas_core(db: Session):
    """Lógica principal compartida"""
    ahora = date.today()
    reservas = (
        db.query(Reserva)
        .filter(Reserva.estado == "aceptada", Reserva.fecha_fin < ahora)
        .all()
    )


    for r in reservas:
        r.estado = "finalizada"


    if reservas:
        db.commit()




def actualizar_reservas_finalizadas(db: Session):
    """Versión usada dentro de endpoints"""
    _actualizar_reservas_core(db)




def actualizar_reservas_automatica():
    """Versión usada por el scheduler (crea su propia sesión)"""
    db = SessionLocal()
    try:
        _actualizar_reservas_core(db)
    finally:
        db.close()