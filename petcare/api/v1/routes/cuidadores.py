from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from petcare.core.database import get_db
from petcare.domain.models.usuario_model import Usuario
from petcare.domain.models.cuidador_model import Cuidador
from petcare.schemas.cuidador_schema import CuidadorCreate
from petcare.core.security import get_current_user
# from petcare.core.map_services import distancia_geodesica
from petcare.core.cuidador_services import buscar_cuidadores_disponibles

cuidadores_router = APIRouter(
    prefix="/cuidadores",
    tags=["Cuidadores"]
)

@cuidadores_router.post("/completar/{usuario_id}")
def completar_datos_cuidador(usuario_id: int, datos: CuidadorCreate,  current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):

    """
    Completa los datos y la descripción del cuidador autenticado. 
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.tipo != "cuidador":
        raise HTTPException(status_code=400, detail="El usuario no es cuidador")
    if usuario.cuidador:
        raise HTTPException(status_code=400, detail="El cuidador ya tiene datos registrados")

    servicios_serializables = [s.value if hasattr(s, 'value') else str(s) for s in datos.servicios]

    dias_serializables = [str(d) for d in datos.dias_no_disponibles] if datos.dias_no_disponibles else None

    cuidador = Cuidador(
        usuario_id=usuario.id,
        descripcion=datos.descripcion,
        servicios=servicios_serializables,
        tarifas=datos.tarifas,
        dias_no_disponibles=dias_serializables
    )

    db.add(cuidador)
    db.commit()
    db.refresh(cuidador)
    return {"mensaje": "Datos del cuidador completados correctamente"}

@cuidadores_router.get("/cercanos")
def obtener_cuidadores_cercanos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    especie: str = Query(...),
    fecha_inicio: date = Query(..., description="Fecha de inicio formato: Año-Mes-Dia"),
    fecha_fin: date = Query(..., description="Fecha de inicio formato: Año-Mes-Dia"),
    radio_km: float = Query(default=None, description="Radio máximo de búsqueda en km (opcional)")
):
    """
    Devuelve cuidadores cercanos al cliente autenticado.
    Si se pasa `radio_km`, solo devuelve los dentro de ese radio.
    """

    # 1️⃣ Validar que sea cliente
    if current_user.tipo != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden buscar cuidadores cercanos."
        )

    if not current_user.lat or not current_user.lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El cliente no tiene coordenadas registradas."
        )

    try:
        resultado = buscar_cuidadores_disponibles(db, current_user, especie, fecha_inicio, fecha_fin, radio_km)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not resultado:
        return {"mensaje": "No se encontraron cuidadores disponibles en las fechas solicitadas."}

    return {
        "cliente": current_user.nombre,
        "cantidad_resultados": len(resultado),
        "cuidadores_disponibles": resultado
    }
    # # 2️⃣ Obtener todos los cuidadores con sus datos de usuario (JOIN)
    # cuidadores = (
    #     db.query(Cuidador)
    #     .join(Usuario)
    #     .filter(Usuario.tipo == "cuidador")
    #     .all()
    # )

    # if not cuidadores:
    #     raise HTTPException(status_code=404, detail="No hay cuidadores registrados.")

    # # 3️⃣ Calcular distancia
    # resultado = []
    # for cuidador in cuidadores:
    #     usuario = cuidador.usuario  # gracias al relationship
    #     if usuario.lat is not None and usuario.lon is not None:
    #         distancia = distancia_geodesica(
    #             (current_user.lat, current_user.lon),
    #             (usuario.lat, usuario.lon)
    #         )
    #         if radio_km is None or distancia <= radio_km:
    #             resultado.append({
    #                 "id": usuario.id,
    #                 "nombre": usuario.nombre,
    #                 "email": usuario.email,
    #                 "direccion": usuario.direccion,
    #                 "map_url": usuario.map_url,
    #                 "descripcion": cuidador.descripcion,
    #                 "servicios": cuidador.servicios,
    #                 "tarifas": cuidador.tarifas,
    #                 "dias_no_disponibles": cuidador.dias_no_disponibles,
    #                 "distancia_km": round(distancia, 2)
    #             })

    # # 4️⃣ Ordenar por distancia ascendente
    # resultado.sort(key=lambda x: x["distancia_km"])

    # if not resultado:
    #     return {"mensaje": "No se encontraron cuidadores dentro del radio especificado."}

    # return {
    #     "cliente": current_user.nombre,
    #     "cantidad_resultados": len(resultado),
    #     "cuidadores_cercanos": resultado
    # }