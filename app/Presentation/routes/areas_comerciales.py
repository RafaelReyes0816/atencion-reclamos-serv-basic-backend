from fastapi import APIRouter, Depends
from app.Presentation.schemas.area_comercial import AreaComercialCreate, AreaComercialUpdate, AreaComercialResponse
from app.Presentation.schemas.dashboard import MensajeResponse
from app.Presentation.dependencies import require_roles, get_service, INTERNO, GESTION
from typing import List

router = APIRouter(prefix="/areas-comerciales", tags=["areas-comerciales"])


@router.get("/", response_model=List[AreaComercialResponse])
def listar_areas(
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["listar_areas"].execute()


@router.post("/", response_model=AreaComercialResponse, status_code=201)
def crear_area(
    area_data: AreaComercialCreate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return use_cases["crear_area"].execute(area_data.model_dump())


@router.get("/{id}", response_model=AreaComercialResponse)
def obtener_area(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["obtener_area"].execute(id)


@router.put("/{id}", response_model=AreaComercialResponse)
def actualizar_area(
    id: int,
    area_data: AreaComercialUpdate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return use_cases["actualizar_area"].execute(id, area_data.model_dump(exclude_unset=True))


@router.delete("/{id}", response_model=MensajeResponse)
def eliminar_area(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    use_cases["eliminar_area"].execute(id)
    return {"message": "Área comercial eliminada", "status": "success"}
