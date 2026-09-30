from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.Presentation.schemas.medidor import (
    MedidorCreate, MedidorUpdate, MedidorResponse, MedidorCiudadanoResponse,
)
from app.Presentation.schemas.dashboard import MensajeResponse
from app.Presentation.dependencies import (
    get_current_user, require_roles, get_service, INTERNO, ADMIN,
)

router = APIRouter(prefix="/medidores", tags=["medidores"])

_INTERNOS = {r.value for r in INTERNO}


def _es_interno(usuario) -> bool:
    return usuario.rol in _INTERNOS


@router.get("/ciudadanos", response_model=List[MedidorCiudadanoResponse])
def listar_ciudadanos_con_medidores(
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    """Ciudadanos y sus medidores. Lo usan los roles internos para registrar a su nombre."""
    return servicio["listar_medidores_ciudadanos"].execute()


@router.get("/", response_model=List[MedidorResponse])
def listar_medidores(
    id_usuario: Optional[int] = None,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Medidores del usuario indicado. Solo los roles internos pueden ver los de otro."""
    if id_usuario is None or id_usuario == current_user.id_usuario:
        return servicio["listar_medidores"].execute(current_user.id_usuario)
    if not _es_interno(current_user):
        raise HTTPException(
            status_code=403, detail="Solo puede consultar sus propios medidores"
        )
    return servicio["listar_medidores"].execute(id_usuario)


@router.post("/", response_model=MedidorResponse, status_code=201)
def crear_medidor(
    medidor_data: MedidorCreate,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*ADMIN)),
):
    """Alta manual. El alta normal ocurre sola al crear la cuenta (agua y luz)."""
    return servicio["crear_medidor"].execute(medidor_data.model_dump())


@router.put("/{id}", response_model=MedidorResponse)
def actualizar_medidor(
    id: int,
    medidor_data: MedidorUpdate,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    """El numero lo corrige el dueno del medidor o cualquier rol interno."""
    medidor = servicio["obtener_medidor"].execute(id)
    if medidor.id_usuario != current_user.id_usuario and not _es_interno(current_user):
        raise HTTPException(
            status_code=403, detail="Solo puede modificar sus propios medidores"
        )
    return servicio["actualizar_medidor"].execute(id, medidor_data.model_dump(exclude_unset=True))


@router.delete("/{id}", response_model=MensajeResponse)
def eliminar_medidor(
    id: int,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*ADMIN)),
):
    servicio["eliminar_medidor"].execute(id)
    return {"message": "Medidor eliminado", "status": "success"}
