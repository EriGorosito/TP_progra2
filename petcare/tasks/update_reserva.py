from datetime import datetime
from sqlalchemy.orm import Session
from petcare.core.database import SessionLocal
from petcare.domain.models.reserva_model import Reserva

def actualizar_reservas_finalizadas():
    db: Session = SessionLocal()
    ahora = datetime.now()

    try:
        reservas = (
            db.query(Reserva)
            .filter(Reserva.estado == "confirmada", Reserva.fecha_fin < ahora)
            .all()
        )

        for r in reservas:
            r.estado = "Finalizada"

        if reservas:
            db.commit()

    finally:
        db.close()
