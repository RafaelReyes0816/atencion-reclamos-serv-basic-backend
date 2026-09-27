from fastapi import APIRouter, Depends, HTTPException
from app.Presentation.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioCambioContrasena, UsuarioResponse,
)
from app.Presentation.schemas.dashboard import MensajeResponse
from app.Presentation.dependencies import get_current_user, require_roles, get_service, GESTION, ADMIN
from app.Domain.Entities.catalogos import Rol
from typing import List

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _es_privilegiado(usuario) -> bool:
    return usuario.rol in {r.value for r in GESTION}


def _verificar_acceso(usuario, objetivo_id: int, objetivo_documento: str = None) -> None:
    """Un ciudadano solo puede verse y editarse a si mismo; gestion/admin pueden ver todos."""
    if _es_privilegiado(usuario):
        return
    if usuario.id_usuario != objetivo_id:
        raise HTTPException(status_code=403, detail="Solo puede consultar o modificar su propia información")
    if objetivo_documento is not None and usuario.documento != objetivo_documento:
        raise HTTPException(status_code=403, detail="Solo puede consultar su propia información")


@router.get("/documento/{documento}", response_model=UsuarioResponse)
def obtener_por_documento(
    documento: str,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    usuario = servicio["obtener_usuario"].execute_por_documento(documento)
    _verificar_acceso(current_user, usuario.id_usuario, documento)
    return usuario


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return servicio["listar_usuarios"].execute()


@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear_usuario(
    usuario_data: UsuarioCreate,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*ADMIN)),
):
    return servicio["crear_usuario"].execute(
        usuario_data.model_dump(exclude={"rol"}),
        rol=usuario_data.rol.value,
    )


@router.get("/{id}", response_model=UsuarioResponse)
def obtener_usuario(
    id: int,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    usuario = servicio["obtener_usuario"].execute(id)
    _verificar_acceso(current_user, usuario.id_usuario)
    return usuario


@router.put("/{id}", response_model=UsuarioResponse)
def actualizar_usuario(
    id: int,
    usuario_data: UsuarioUpdate,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    _verificar_acceso(current_user, id)
    cambios = usuario_data.model_dump(exclude_unset=True)
    if "rol" in cambios and current_user.rol not in {r.value for r in ADMIN}:
        cambios.pop("rol")
    return servicio["actualizar_usuario"].execute(id, cambios)


@router.put("/{id}/contrasena", response_model=MensajeResponse)
def cambiar_contrasena(
    id: int,
    datos: UsuarioCambioContrasena,
    servicio=Depends(get_service),
    current_user=Depends(get_current_user),
):
    if current_user.id_usuario != id:
        raise HTTPException(status_code=403, detail="Solo puede cambiar su propia contraseña")
    servicio["cambiar_contrasena"].execute(id, datos.contrasena_actual, datos.contrasena_nueva)
    return {"message": "Contraseña actualizada correctamente", "status": "success"}


@router.delete("/{id}", response_model=MensajeResponse)
def eliminar_usuario(
    id: int,
    servicio=Depends(get_service),
    current_user=Depends(require_roles(*ADMIN)),
):
    servicio["eliminar_usuario"].execute(id)
    return {"message": "Usuario eliminado", "status": "success"}
