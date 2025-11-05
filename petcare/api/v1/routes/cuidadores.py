from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from petcare.core.database import get_db
from petcare.domain.models.usuario_model import Usuario
from petcare.domain.models.cuidador_model import Cuidador
from petcare.schemas.cuidador_schema import CuidadorCreate
from petcare.core.security import get_current_user

cuidadores_router = APIRouter(
    prefix="/cuidadores",
    tags=["Cuidadores"]
)

@cuidadores_router.post("/completar/{usuario_id}")
def completar_datos_cuidador(usuario_id: int, datos: CuidadorCreate,  current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
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
