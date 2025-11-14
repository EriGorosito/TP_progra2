from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from sqlalchemy.dialects.postgresql import JSONB
from fastapi import HTTPException

from petcare.core.resena_services import get_cuidador_puntaje, get_reviews_by_cuidador
from petcare.infraestructura.models.usuario_model import Cuidador, Usuario
from petcare.infraestructura.models.reserva_model import Reserva
from petcare.core.map_services import distancia_geodesica


def completar_datos_cuidador_service(
    db: Session,
    usuario_id: int,
    current_user: Usuario,
    datos
):
    """
    Completa o actualiza la información adicional de un cuidador.

    Esta función verifica que:
    - El usuario con el `usuario_id` exista.
    - El usuario sea de tipo cuidador.
    - El usuario autenticado tenga permiso para modificar estos datos.

    Luego actualiza la descripción, servicios, tarifas y días no disponibles
    asociados al cuidador.
    """

    # Validar usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.tipo != "cuidador":
        raise HTTPException(status_code=400, detail="El usuario no es cuidador")
    
    # Validar autorización
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para modificar datos de otro usuario"
        )

    # 3. Obtener cuidador
    cuidador = db.query(Cuidador).filter(Cuidador.id == usuario_id).first()

    if not cuidador:
        raise HTTPException(status_code=404, detail="Cuidador no encontrado")

    # 4. Serializar servicios
    servicios_serializables = [
        s.value if hasattr(s, "value") else str(s)
        for s in datos.servicios
    ]

    # 5. Serializar días
    dias_serializables = (
        [str(d) for d in datos.dias_no_disponibles]
        if datos.dias_no_disponibles else None
    )

    # 6. Actualizar campos
    cuidador.descripcion = datos.descripcion
    cuidador.servicios = servicios_serializables
    cuidador.tarifas = datos.tarifas
    cuidador.dias_no_disponibles = dias_serializables

    # 7. Guardar cambios
    db.commit()
    db.refresh(cuidador)

    return cuidador


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

    # Convertimos todas las especies buscadas a minúscula.
    especies_list_lower = [e.lower() for e in especies_list]
    
    # Construimos el filtro según la base de datos
    if "postgresql" in dialecto:
        # Render/Supabase: Usamos operador JSONB '?'
        for e in especies_list_lower: # <-- Usamos la lista en minúscula
            filtros_especie.append(Cuidador.servicios.cast(JSONB).op('?')(e))
    else:
        # Local SQLite: Usamos LIKE (contains)
        for e in especies_list_lower: # <-- Usamos la lista en minúscula
            filtros_especie.append(Cuidador.servicios.contains(e))

    especie_filter = or_(*filtros_especie)

    # --- B. Consulta Inicial ---
    # 1. Consultamos Cuidador.

    query = db.query(Cuidador)
    
    # 2. Filtramos por tipo.

    query = query.filter(func.lower(Cuidador.tipo) == 'cuidador')
    
    # 3. Aplicamos el filtro de especies.
    # Esto previene el error 'jsonb ~~ text' de PostgreSQL
    query = query.filter(especie_filter)

    # 4. Ejecutamos la consulta.
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
        dias_no_disp = cuidador.dias_no_disponibles or [] # lista de strings: ["2029-12-05"]
    
        # Generamos la lista de fechas que el cliente necesita
        delta = (fecha_fin - fecha_inicio).days + 1
        fechas_solicitadas_str = [(fecha_inicio + timedelta(days=i)).isoformat() for i in range(delta)]
    
    # Si ALGUNA fecha solicitada está en la lista de no disponibles, saltamos este cuidador
        if any(dia_str in dias_no_disp for dia_str in fechas_solicitadas_str):
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
