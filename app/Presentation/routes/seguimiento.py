from fastapi import APIRouter, Depends
from app.Presentation.schemas.orden_trabajo import OrdenTrabajoCreate, OrdenTrabajoUpdate, OrdenTrabajoResponse
from app.Presentation.schemas.avance import AvanceCreate, AvanceResponse
from app.Presentation.schemas.derivacion import DerivacionCreate, DerivacionUpdate, DerivacionResponse
from app.Presentation.schemas.dashboard import MensajeResponse
from app.Presentation.dependencies import require_roles, get_service, INTERNO, GESTION
from typing import List

router = APIRouter(prefix="/seguimiento", tags=["seguimiento"])


@router.get("/ordenes", response_model=List[OrdenTrabajoResponse])
def listar_ordenes(
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["listar_ordenes"].execute()


@router.get("/ordenes/reclamo/{id_reclamo}", response_model=OrdenTrabajoResponse)
def obtener_por_reclamo(
    id_reclamo: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["obtener_orden"].execute_por_reclamo(id_reclamo)


@router.post("/ordenes", response_model=OrdenTrabajoResponse, status_code=201)
def crear_orden(
    orden_data: OrdenTrabajoCreate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["crear_orden"].execute(orden_data.model_dump())


@router.get("/ordenes/{id}", response_model=OrdenTrabajoResponse)
def obtener_orden(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["obtener_orden"].execute(id)


@router.put("/ordenes/{id}", response_model=OrdenTrabajoResponse)
def actualizar_orden(
    id: int,
    orden_data: OrdenTrabajoUpdate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["actualizar_orden"].execute(id, orden_data.model_dump(exclude_unset=True))


@router.delete("/ordenes/{id}", response_model=MensajeResponse)
def eliminar_orden(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    use_cases["eliminar_orden"].execute(id)
    return {"message": "Orden de trabajo eliminada", "status": "success"}


@router.get("/avances/{id_orden}", response_model=List[AvanceResponse])
def listar_avances(
    id_orden: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    use_cases["obtener_orden"].execute(id_orden)
    return use_cases["listar_avances"].execute(id_orden)


@router.post("/avances", response_model=AvanceResponse, status_code=201)
def crear_avance(
    avance_data: AvanceCreate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["crear_avance"].execute(avance_data.model_dump())


@router.get("/derivaciones/reclamo/{id_reclamo}", response_model=DerivacionResponse)
def obtener_derivacion_por_reclamo(
    id_reclamo: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["obtener_derivacion"].execute_por_reclamo(id_reclamo)


@router.get("/derivaciones/{id}", response_model=DerivacionResponse)
def obtener_derivacion(
    id: int,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["obtener_derivacion"].execute(id)


@router.post("/derivaciones", response_model=DerivacionResponse, status_code=201)
def crear_derivacion(
    derivacion_data: DerivacionCreate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["crear_derivacion"].execute(derivacion_data.model_dump())


@router.put("/derivaciones/{id}", response_model=DerivacionResponse)
def actualizar_derivacion(
    id: int,
    derivacion_data: DerivacionUpdate,
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return use_cases["actualizar_derivacion"].execute(id, derivacion_data.model_dump(exclude_unset=True))
