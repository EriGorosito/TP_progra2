# petcare/domain/models/reserva_model.py
from sqlalchemy import Column, Integer, ForeignKey, Date, String
from petcare.core.database import Base

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    cuidador_id = Column(Integer, ForeignKey("usuarios.id"))
    mascota_id = Column(Integer, ForeignKey("mascotas.id"))
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(String, default="pendiente")  # pendiente, confirmada, rechazada
