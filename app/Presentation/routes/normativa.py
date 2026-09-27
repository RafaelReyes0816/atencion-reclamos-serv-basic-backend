from fastapi import APIRouter, Depends
from app.Presentation.schemas.normativa import (
    NormativaCreate, NormativaUpdate, NormativaFiltros, NormativaResponse
)
from app.Presentation.schemas.dashboard import MensajeResponse
from app.Presentation.dependencies import require_roles, get_service, INTERNO, GESTION
from app.Domain.Entities.catalogos import Servicio, Categoria, Urgencia
from typing import List

router = APIRouter(prefix="/normativa", tags=["normativa"])


@router.get("/vigente", response_model=NormativaResponse)
def obtener_vigente(
    servicio: Servicio,
    categoria: Categoria,
    urgencia: Urgencia,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["obtener_normativa"].execute_vigente(servicio, categoria, urgencia)


@router.get("/", response_model=List[NormativaResponse])
def listar_normativa(
    filtros: NormativaFiltros = Depends(),
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["listar_normativa"].execute(**filtros.model_dump(exclude_none=True))


@router.post("/", response_model=NormativaResponse, status_code=201)
def crear_normativa(
    normativa_data: NormativaCreate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return use_cases["crear_normativa"].execute(normativa_data.model_dump())


@router.get("/{id}", response_model=NormativaResponse)
def obtener_normativa(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["obtener_normativa"].execute(id)


@router.put("/{id}", response_model=NormativaResponse)
def actualizar_normativa(
    id: int,
    normativa_data: NormativaUpdate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return use_cases["actualizar_normativa"].execute(id, normativa_data.model_dump(exclude_unset=True))


@router.delete("/{id}", response_model=MensajeResponse)
def eliminar_normativa(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    use_cases["eliminar_normativa"].execute(id)
    return {"message": "Normativa eliminada", "status": "success"}
