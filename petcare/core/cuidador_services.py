from sqlalchemy.orm import Session
from datetime import date

from petcare.core.resena_services import get_cuidador_puntaje, get_reviews_by_cuidador
from petcare.infraestructura.models.usuario_model import Cuidador
from petcare.infraestructura.models.reserva_model import Reserva
from petcare.core.map_services import distancia_geodesica
from sqlalchemy import or_


def cuidador_disponible(db: Session, cuidador_id: int, fecha_inicio: date, fecha_fin: date) -> bool:
    """
    Verifica si el cuidador está disponible entre las fechas dadas.
    Devuelve False si ya tiene reservas en ese rango.
    """
    reservas = db.query(Reserva).filter(
        Reserva.cuidador_id == cuidador_id,
        Reserva.estado.in_(["pendiente", "confirmada"]),  # opcional, según tu modelo
        Reserva.fecha_inicio <= fecha_fin,
        Reserva.fecha_fin >= fecha_inicio
    ).all()

    return len(reservas) == 0


def buscar_cuidadores_disponibles(
    db: Session, 
    cliente, 
    especies: list[str], 
    fecha_inicio: date, 
    fecha_fin: date, 
    radio_km: float = None
):
    """
    Busca cuidadores disponibles que coincidan con la especie, la ubicación 
    y la disponibilidad horaria del servicio solicitado.
    """
    if not cliente.lat or not cliente.lon:
        raise ValueError("El cliente no tiene coordenadas registradas.")

    if isinstance(especies, list):
        # Crear la cláusula OR para buscar cualquiera de las especies en la columna servicios
        especie_filter = or_(*[Cuidador.servicios.contains(e) for e in especies])
    else:
        especie_filter = Cuidador.servicios.contains(especies)

    cuidadores = db.query(Cuidador).filter(especie_filter).all()

    resultado = []

    for cuidador in cuidadores:
        promedio = get_cuidador_puntaje(db, cuidador.id)
        resena = get_reviews_by_cuidador(db, cuidador.id)
        if cuidador.lat is None or cuidador.lon is None:
            continue

        # Calcular distancia
        distancia = distancia_geodesica((cliente.lat, cliente.lon), (cuidador.lat, cuidador.lon))
        if radio_km is not None and distancia > radio_km:
            continue

        # Verificar reservas existentes
        reservas_ocupadas = (
            db.query(Reserva)
            .filter(
                Reserva.cuidador_id == cuidador.id,
                Reserva.estado != "cancelada",
                Reserva.fecha_inicio <= fecha_fin,
                Reserva.fecha_fin >= fecha_inicio
            )
            .count()
        )
        if reservas_ocupadas > 0:
            continue

        # Verificar días no disponibles
        dias_no_disp = cuidador.dias_no_disponibles or []
        if any(str(d) in dias_no_disp for d in range((fecha_fin - fecha_inicio).days + 1)):
            continue

        resultado.append({
            "id": cuidador.id,
            "nombre": cuidador.nombre,
            "email": cuidador.email,
            "direccion": cuidador.direccion,
            "descripcion": cuidador.descripcion,
            "tarifas": cuidador.tarifas,
            "distancia_km": round(distancia, 2),
            "puntaje": promedio,
            "reseñas": resena
        })

    #Oredenar por distancia
    return sorted(resultado, key=lambda x: x["distancia_km"])




