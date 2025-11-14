from sqlalchemy.orm import Session
from datetime import date, timedelta
# Importación necesaria para que PostgreSQL entienda columnas JSONB
from sqlalchemy.dialects.postgresql import JSONB

from petcare.core.resena_services import get_cuidador_puntaje, get_reviews_by_cuidador
from petcare.infraestructura.models.usuario_model import Usuario, Cuidador
from petcare.infraestructura.models.reserva_model import Reserva
from petcare.core.map_services import distancia_geodesica
from sqlalchemy import or_

'''
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
'''

def cuidador_disponible(db: Session, cuidador_id: int, fecha_inicio: date, fecha_fin: date) -> bool:
    """
    Verifica disponibilidad REAL:
    1. Que no tenga reservas activas en ese rango.
    2. Que no tenga días bloqueados manualmente en 'dias_no_disponibles'.
    """
    
    # --- 1. Verificar Reservas Existentes (Solapamiento) ---
    reservas = db.query(Reserva).filter(
        Reserva.cuidador_id == cuidador_id,
        Reserva.estado.in_(["pendiente", "aceptada", "confirmada"]), 
        Reserva.fecha_inicio <= fecha_fin,
        Reserva.fecha_fin >= fecha_inicio
    ).count()

    if reservas > 0:
        return False # Ya tiene una reserva activa

    # --- 2. Verificar Días Bloqueados Manualmente ---
    cuidador = db.query(Cuidador).filter(Cuidador.id == cuidador_id).first()
    if not cuidador:
        return False
        
    dias_bloqueados = cuidador.dias_no_disponibles or [] # Lista de strings ["2025-05-13"]
    
    # Generar fechas del rango solicitado
    delta_dias = (fecha_fin - fecha_inicio).days + 1
    rango_fechas = [fecha_inicio + timedelta(days=i) for i in range(delta_dias)]

    for dia in rango_fechas:
        if dia.isoformat() in dias_bloqueados:
            return False # El cuidador bloqueó este día

    return True


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
    y la disponibilidad horaria. Compatible con SQLite y PostgreSQL.
    """
    if not cliente.lat or not cliente.lon:
        raise ValueError("El cliente no tiene coordenadas registradas.")

    # --- A. Lógica de Filtro Híbrida (SQLite vs Postgres) ---
    dialecto = db.bind.dialect.name 
    filtros_especie = []

    # Aseguramos que sea lista
    if not isinstance(especies, list):
        especies_list = [especies]
    else:
        especies_list = especies

    # Construimos el filtro según la base de datos
    if "postgresql" in dialecto:
        # Render/Supabase: Usamos operador JSONB '?'
        for e in especies_list:
            filtros_especie.append(Cuidador.servicios.cast(JSONB).op('?')(e))
    else:
        # Local SQLite: Usamos LIKE (contains)
        for e in especies_list:
            filtros_especie.append(Cuidador.servicios.contains(e))

    especie_filter = or_(*filtros_especie)

    # --- B. Consulta Inicial ---
    # 1. Empezamos consultando la tabla Cuidador
    query = db.query(Cuidador)
    
    # 2. La unimos (JOIN) con la tabla Usuario usando la FK correcta
    query = query.join(Usuario, Cuidador.id == Usuario.id)
    
    # 3. Filtramos para asegurar que solo traemos usuarios de tipo 'cuidador'
    query = query.filter(Usuario.tipo == 'cuidador')
    
    # 4. Ahora sí, aplicamos el filtro de especies (que ya funciona)
    query = query.filter(especie_filter)

    cuidadores = query.all()

    resultado = []

    # Generar rango de fechas una sola vez para el bucle
    delta_dias = (fecha_fin - fecha_inicio).days + 1
    fechas_solicitadas_str = [(fecha_inicio + timedelta(days=i)).isoformat() for i in range(delta_dias)]

    for cuidador in cuidadores:
        # Filtro básico de coordenadas
        if cuidador.lat is None or cuidador.lon is None:
            continue

        # Calcular distancia
        distancia = distancia_geodesica((cliente.lat, cliente.lon), (cuidador.lat, cuidador.lon))
        if radio_km is not None and distancia > radio_km:
            continue

        # --- C. Validaciones de Disponibilidad ---
        
        # 1. Verificar reservas existentes (Solapamiento)
        reservas_ocupadas = (
            db.query(Reserva)
            .filter(
                Reserva.cuidador_id == cuidador.id,
                Reserva.estado.in_(["pendiente", "aceptada", "confirmada"]), # Excluimos canceladas/finalizadas
                Reserva.fecha_inicio <= fecha_fin,
                Reserva.fecha_fin >= fecha_inicio
            )
            .count()
        )
        if reservas_ocupadas > 0:
            continue

        # 2. Verificar días no disponibles (Manuales)
        # (Arreglado: comparamos fechas reales, no números del range)
        dias_no_disp = cuidador.dias_no_disponibles or []
        
        # Si alguna fecha solicitada está en la lista de no disponibles, saltamos este cuidador
        if any(dia in dias_no_disp for dia in fechas_solicitadas_str):
            continue

        # --- D. Obtener datos extra y armar respuesta ---
        promedio = get_cuidador_puntaje(db, cuidador.id)
        resena = get_reviews_by_cuidador(db, cuidador.id)

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

    # Ordenar por distancia
    return sorted(resultado, key=lambda x: x["distancia_km"])

'''
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
'''



