from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.security import decode_access_token
from app.Infraestructura.repositories.usuario_repository import UsuarioRepository
from app.Infraestructura.repositories.reclamo_repository import ReclamoRepository
from app.Infraestructura.repositories.normativa_plazo_repository import NormativaPlazoRepository
from app.Infraestructura.repositories.orden_trabajo_repository import OrdenTrabajoRepository
from app.Infraestructura.repositories.avance_repository import AvanceRepository
from app.Infraestructura.repositories.derivacion_comercial_repository import DerivacionComercialRepository
from app.Infraestructura.repositories.cuadrilla_repository import CuadrillaRepository
from app.Infraestructura.repositories.area_comercial_repository import AreaComercialRepository
from app.Infraestructura.repositories.reporte_repository import ReporteRepository
from app.Application.usecase.usuario.listar_usuarios import ListarUsuariosUseCase
from app.Application.usecase.usuario.obtener_usuario import ObtenerUsuarioUseCase
from app.Application.usecase.usuario.crear_usuario import CrearUsuarioUseCase
from app.Application.usecase.usuario.actualizar_usuario import ActualizarUsuarioUseCase
from app.Application.usecase.reclamo.listar_reclamos import ListarReclamosUseCase
from app.Application.usecase.reclamo.obtener_reclamo import ObtenerReclamoUseCase
from app.Application.usecase.reclamo.crear_reclamo import CrearReclamoUseCase
from app.Application.usecase.reclamo.actualizar_reclamo import ActualizarReclamoUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    usuario_repo = UsuarioRepository(db)
    usuario = usuario_repo.get_by_id(payload.get("sub"))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return usuario


def get_service(db: Session = Depends(get_db)):
    usuario_repo = UsuarioRepository(db)
    reclamo_repo = ReclamoRepository(db)
    normativa_repo = NormativaPlazoRepository(db)
    orden_repo = OrdenTrabajoRepository(db)
    avance_repo = AvanceRepository(db)
    derivacion_repo = DerivacionComercialRepository(db)
    cuadrilla_repo = CuadrillaRepository(db)
    area_repo = AreaComercialRepository(db)
    reporte_repo = ReporteRepository(db)

    return {
        "listar_usuarios": ListarUsuariosUseCase(usuario_repo),
        "obtener_usuario": ObtenerUsuarioUseCase(usuario_repo),
        "crear_usuario": CrearUsuarioUseCase(usuario_repo),
        "actualizar_usuario": ActualizarUsuarioUseCase(usuario_repo),
        "listar_reclamos": ListarReclamosUseCase(reclamo_repo),
        "obtener_reclamo": ObtenerReclamoUseCase(reclamo_repo),
        "crear_reclamo": CrearReclamoUseCase(reclamo_repo, usuario_repo),
        "actualizar_reclamo": ActualizarReclamoUseCase(reclamo_repo),
    }
