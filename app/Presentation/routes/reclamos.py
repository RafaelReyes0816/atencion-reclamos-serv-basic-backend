from fastapi import APIRouter, Depends, HTTPException
from app.Presentation.schemas.reclamo import (
    ReclamoCreate, ReclamoUpdate, ReclamoClasificar, ReclamoFiltros,
    ReclamoAsignarPlazo, ReclamoResolver, ReclamoCerrar,
    ReclamoContactoUpdate, ReclamoResponse, ComprobanteResponse,
)
from app.Presentation.schemas.dashboard import MensajeResponse
from app.Presentation.dependencies import get_current_user, require_roles, get_service, INTERNO, GESTION, ADMIN
from app.Domain.Entities.catalogos import Rol
from typing import List

router = APIRouter(prefix="/reclamos", tags=["reclamos"])

_INTERNOS = {r.value for r in INTERNO}


def _es_interno(usuario) -> bool:
    return usuario.rol in _INTERNOS


def _verificar_lectura(usuario, reclamo) -> None:
    """El ciudadano solo accede a sus propios reclamos; el personal interno a todos."""
    if _es_interno(usuario) or reclamo.id_usuario == usuario.id_usuario:
        return
    raise HTTPException(status_code=403, detail="Solo puede consultar sus propios reclamos")


@router.get("/estado/{id_o_doc}")
def consultar_estado(id_o_doc: str, servicio=Depends(get_service)):
    reclamo = servicio["consultar_estado_reclamo"].execute(id_o_doc)
    return {
        "id_reclamo": reclamo.id_reclamo,
        "estado": reclamo.estado,
        "fecha_tope": reclamo.fecha_tope,
    }


@router.get("/", response_model=List[ReclamoResponse])
def listar_reclamos(
    filtros: ReclamoFiltros = Depends(),
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    filtros_dict = filtros.model_dump(exclude_none=True)
    if not _es_interno(current_user):
        filtros_dict["id_usuario"] = current_user.id_usuario
    return servicio["listar_reclamos"].execute(**filtros_dict)


@router.post("/", response_model=ReclamoResponse, status_code=201)
def crear_reclamo(
    reclamo_data: ReclamoCreate,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    if not _es_interno(current_user) and reclamo_data.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Solo puede registrar reclamos a su nombre")
    return servicio["crear_reclamo"].execute(reclamo_data.model_dump())


@router.get("/{id}", response_model=ReclamoResponse)
def obtener_reclamo(
    id: int,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    reclamo = servicio["obtener_reclamo"].execute(id)
    _verificar_lectura(current_user, reclamo)
    return reclamo


@router.put("/{id}", response_model=ReclamoResponse)
def actualizar_reclamo(
    id: int,
    reclamo_data: ReclamoUpdate,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return servicio["actualizar_reclamo"].execute(id, reclamo_data.model_dump(exclude_unset=True))


@router.put("/{id}/clasificar", response_model=ReclamoResponse)
def clasificar_reclamo(
    id: int,
    clasificacion: ReclamoClasificar,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return servicio["clasificar_reclamo"].execute(
        id, clasificacion.servicio, clasificacion.categoria, clasificacion.urgencia
    )


@router.put("/{id}/asignar-plazo", response_model=ReclamoResponse)
def asignar_plazo(
    id: int,
    plazo: ReclamoAsignarPlazo,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return servicio["asignar_plazo"].execute(id, plazo.id_normativa, plazo.fecha_tope)


@router.put("/{id}/resolver", response_model=ReclamoResponse)
def resolver_reclamo(
    id: int,
    resolucion: ReclamoResolver,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*INTERNO)),
):
    return servicio["resolver_reclamo"].execute(id, resolucion.resultado)


@router.put("/{id}/cerrar", response_model=ReclamoResponse)
def cerrar_reclamo(
    id: int,
    cierre: ReclamoCerrar,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return servicio["cerrar_reclamo"].execute(id, cierre.resultado)


@router.get("/{id}/comprobante", response_model=ComprobanteResponse)
def obtener_comprobante(
    id: int,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    reclamo = servicio["obtener_reclamo"].execute(id)
    _verificar_lectura(current_user, reclamo)
    return reclamo


@router.put("/{id}/contacto", response_model=MensajeResponse)
def actualizar_contacto(
    id: int,
    contacto: ReclamoContactoUpdate,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    reclamo = servicio["obtener_reclamo"].execute(id)
    _verificar_lectura(current_user, reclamo)
    servicio["actualizar_contacto"].execute(id, contacto.telefono, contacto.email)
    return {"message": "Contacto actualizado", "status": "success"}


@router.delete("/{id}", response_model=MensajeResponse)
def eliminar_reclamo(
    id: int,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*ADMIN)),
):
    servicio["eliminar_reclamo"].execute(id)
    return {"message": "Reclamo eliminado", "status": "success"}
