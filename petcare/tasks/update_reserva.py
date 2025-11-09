from datetime import date
from sqlalchemy.orm import Session
from petcare.core.database import SessionLocal
from petcare.domain.models.reserva_model import Reserva

def actualizar_reservas_finalizadas():
    db: Session = SessionLocal()
    ahora = date.today()

    try:
        reservas = (
            db.query(Reserva)
            .filter(Reserva.estado == "aceptada", Reserva.fecha_fin < ahora)
            .all()
        )

        for r in reservas:
            r.estado = "finalizada"

        if reservas:
            db.commit()

    finally:
        db.close()
