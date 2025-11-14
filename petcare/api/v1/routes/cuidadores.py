from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

# Importaciones locales
from petcare.core.database import get_db
from petcare.core.security import get_current_user
from petcare.core.cuidador_services import buscar_cuidadores_disponibles
from petcare.infraestructura.models.usuario_model import Usuario
from petcare.infraestructura.models.usuario_model import Cuidador
from petcare.schemas.cuidador_schema import CuidadorCreate


cuidadores_router = APIRouter(
    prefix="/cuidadores",
    tags=["Cuidadores"]
)


@cuidadores_router.post("/completar/{usuario_id}")
def completar_datos_cuidador(
    usuario_id: int,
    datos: CuidadorCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Completa o crea los datos del perfil del cuidador autenticado.
    """
    
    # 1. Validar Usuario (Esto está perfecto)
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.tipo != "cuidador":
        raise HTTPException(status_code=400, detail="El usuario no es cuidador")
    
    # Validación de Seguridad
    if current_user.id != usuario_id:
        raise HTTPException(status_code=403, detail="No autorizado para editar este perfil")

    # --- 2. OBTENER O CREAR CUIDADOR (¡EL ARREGLO!) ---
    
    # Buscamos el perfil usando la CLAVE FORÁNEA (FK)
    cuidador = db.query(Cuidador).filter(Cuidador.usuario_id == usuario_id).first()

    if not cuidador:
        # Si no existe, lo creamos y lo vinculamos con la FK
        cuidador = Cuidador(usuario_id=usuario_id) 
        db.add(cuidador)

    # 3. Serializar datos (Perfecto)
    servicios_serializables = [
        s.value if hasattr(s, 'value') else str(s)
        for s in datos.servicios
    ]
    dias_serializables = (
        [str(d) for d in datos.dias_no_disponibles]
        if datos.dias_no_disponibles else None
    )

    # 4. Actualizar atributos (Perfecto)
    cuidador.descripcion = datos.descripcion
    cuidador.servicios = servicios_serializables
    cuidador.tarifas = datos.tarifas
    cuidador.dias_no_disponibles = dias_serializables

    try:
        # 5. Persistir cambios
        db.commit()
        db.refresh(cuidador)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar datos: {e}")

    return {"mensaje": "Datos del cuidador completados correctamente"}


@cuidadores_router.get("/cercanos")
def obtener_cuidadores_cercanos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    especies: list[str] = Query(..., description="Lista de especies: perro, gato, etc."),
    fecha_inicio: date = Query(..., description="Fecha de inicio formato: Año-Mes-Dia"),
    fecha_fin: date = Query(..., description="Fecha de fin formato: Año-Mes-Dia"),
    radio_km: float = Query(
        default=None, description="Radio máximo de búsqueda en km (opcional)"
    )
):
    """
    Devuelve cuidadores cercanos al cliente autenticado.
    Si se pasa `radio_km`, solo devuelve los dentro de ese radio.
    """
    # 1. Validar que sea cliente
    if current_user.tipo.lower() != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden buscar cuidadores cercanos."
        )

    if not current_user.lat or not current_user.lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El cliente no tiene coordenadas registradas."
        )

    # 2. Llamar al servicio de búsqueda
    try:
        resultado = buscar_cuidadores_disponibles(
            db, current_user, especies, fecha_inicio, fecha_fin, radio_km
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not resultado:
        return {"mensaje": "No se encontraron cuidadores disponibles en las fechas solicitadas."}

    # 3. Formatear respuesta
    return {
        "cliente": current_user.nombre,
        "cantidad_resultados": len(resultado),
        "cuidadores_disponibles": resultado
    }


