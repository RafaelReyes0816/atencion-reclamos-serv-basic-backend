from fastapi import APIRouter, Depends
from app.Presentation.schemas.cuadrilla import CuadrillaCreate, CuadrillaUpdate, CuadrillaResponse
from app.Presentation.schemas.dashboard import MensajeResponse
from app.Presentation.dependencies import require_roles, get_service, INTERNO, GESTION
from app.Domain.Entities.catalogos import Servicio
from typing import List

router = APIRouter(prefix="/cuadrillas", tags=["cuadrillas"])


@router.get("/disponibles/{especialidad}", response_model=List[CuadrillaResponse])
def obtener_disponibles(
    especialidad: Servicio,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["listar_cuadrillas"].execute_disponibles(especialidad)


@router.get("/", response_model=List[CuadrillaResponse])
def listar_cuadrillas(
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["listar_cuadrillas"].execute()


@router.post("/", response_model=CuadrillaResponse, status_code=201)
def crear_cuadrilla(
    cuadrilla_data: CuadrillaCreate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return use_cases["crear_cuadrilla"].execute(cuadrilla_data.model_dump())


@router.get("/{id}", response_model=CuadrillaResponse)
def obtener_cuadrilla(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["obtener_cuadrilla"].execute(id)


@router.put("/{id}", response_model=CuadrillaResponse)
def actualizar_cuadrilla(
    id: int,
    cuadrilla_data: CuadrillaUpdate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return use_cases["actualizar_cuadrilla"].execute(id, cuadrilla_data.model_dump(exclude_unset=True))


@router.delete("/{id}", response_model=MensajeResponse)
def eliminar_cuadrilla(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    use_cases["eliminar_cuadrilla"].execute(id)
    return {"message": "Cuadrilla eliminada", "status": "success"}
