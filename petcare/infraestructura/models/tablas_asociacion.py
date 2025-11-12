# petcare/infraestructura/models/tablas_asociacion.py

from sqlalchemy import Column, Integer, ForeignKey, Table
from petcare.core.database import Base # O como importes tu Base

# Esta tabla ahora vive aquí, en un lugar neutral
reserva_mascota = Table(
    "reserva_mascota",
    Base.metadata,
    Column("reserva_id", Integer, ForeignKey("reservas.id"), primary_key=True),
    Column("mascota_id", Integer, ForeignKey("mascotas.id"), primary_key=True)
)