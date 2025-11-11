from petcare.core.resena_services import get_cuidador_puntaje, get_reviews_by_cuidador
from sqlalchemy.orm import Session

from datetime import date
from petcare.domain.models.cuidador_model import Cuidador
from petcare.domain.models.reserva_model import Reserva
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


def buscar_cuidadores_disponibles(db: Session, cliente, especies: list[str], fecha_inicio: date, fecha_fin: date, radio_km: float = None):
    if not cliente.lat or not cliente.lon:
        raise ValueError("El cliente no tiene coordenadas registradas.")

    # Buscar cuidadores que cuiden esa especie
    # cuidadores = (
    #     db.query(Cuidador)
    #     .join(Cuidador.usuario)
    #     .filter(
    #         Cuidador.servicios.contains(especie)
    #     )
    #     .all()
    # )
    if isinstance(especies, list):
        especie_filter = or_(*[Cuidador.servicios.contains(e) for e in especies])
    else:
        especie_filter = Cuidador.servicios.contains(especies)

    cuidadores = (
        db.query(Cuidador)
        .join(Cuidador.usuario)
<<<<<<< HEAD
        .filter(especie_filter)
=======
        .filter(
        Cuidador.servicios.op('?')(especie)
        )
>>>>>>> origin/main
        .all()
    )

    resultado = []
    for cuidador in cuidadores:
        usuario = cuidador.usuario
        promedio = get_cuidador_puntaje(db, usuario.id)
        resena = get_reviews_by_cuidador(db, usuario.id)
        if usuario.lat is None or usuario.lon is None:
            continue

        # Calcular distancia
        distancia = distancia_geodesica((cliente.lat, cliente.lon), (usuario.lat, usuario.lon))
        if radio_km is not None and distancia > radio_km:
            continue

        # Verificar reservas existentes
        reservas_ocupadas = (
            db.query(Reserva)
            .filter(
                Reserva.cuidador_id == usuario.id,
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
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "direccion": usuario.direccion,
            "descripcion": cuidador.descripcion,
            "tarifas": cuidador.tarifas,
            "distancia_km": round(distancia, 2),
            "puntaje": promedio,
            "reseñas": resena
        })

    return sorted(resultado, key=lambda x: x["distancia_km"])
