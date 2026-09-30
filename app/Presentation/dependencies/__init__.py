from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.security import decode_access_token
from app.Infraestructura.repositories.usuario_repository import UsuarioRepository
from app.Infraestructura.repositories.medidor_repository import MedidorRepository
from app.Infraestructura.repositories.reclamo_repository import ReclamoRepository
from app.Infraestructura.repositories.normativa_plazo_repository import NormativaPlazoRepository
from app.Infraestructura.repositories.orden_trabajo_repository import OrdenTrabajoRepository
from app.Infraestructura.repositories.avance_repository import AvanceRepository
from app.Infraestructura.repositories.derivacion_comercial_repository import DerivacionComercialRepository
from app.Infraestructura.repositories.cuadrilla_repository import CuadrillaRepository
from app.Infraestructura.repositories.area_comercial_repository import AreaComercialRepository
from app.Infraestructura.repositories.reporte_repository import ReporteRepository
from app.Application.usecase.usuario.listar_usuarios import ListarUsuariosUseCase
from app.Application.usecase.usuario.obtener_usuario import ObtenerUsuarioUseCase, EliminarUsuarioUseCase
from app.Application.usecase.usuario.crear_usuario import CrearUsuarioUseCase
from app.Application.usecase.usuario.actualizar_usuario import ActualizarUsuarioUseCase
from app.Application.usecase.usuario.cambiar_contrasena import CambiarContrasenaUseCase
from app.Application.usecase.medidor.gestionar_medidor import (
    ListarMedidoresUseCase, ObtenerMedidorUseCase, ListarMedidoresDeCiudadanosUseCase,
    CrearMedidorUseCase, ActualizarMedidorUseCase, EliminarMedidorUseCase,
    AsignarMedidoresPorDefectoUseCase,
)
from app.Application.usecase.reclamo.listar_reclamos import ListarReclamosUseCase
from app.Application.usecase.reclamo.obtener_reclamo import (
    ObtenerReclamoUseCase, ClasificarReclamoUseCase, ConsultarEstadoReclamoUseCase,
)
from app.Application.usecase.reclamo.crear_reclamo import CrearReclamoUseCase
from app.Application.usecase.reclamo.actualizar_reclamo import ActualizarReclamoUseCase, EliminarReclamoUseCase
from app.Application.usecase.reclamo.asignar_plazo import AsignarPlazoUseCase
from app.Application.usecase.reclamo.resolver_reclamo import ResolverReclamoUseCase, CerrarReclamoUseCase
from app.Application.usecase.reclamo.actualizar_contacto import ActualizarContactoUseCase
from app.Application.usecase.orden_trabajo.gestionar_orden import (
    ListarOrdenesUseCase, ObtenerOrdenUseCase, CrearOrdenUseCase,
    ActualizarOrdenUseCase, EliminarOrdenUseCase,
)
from app.Application.usecase.avance.gestionar_avance import ListarAvancesUseCase, CrearAvanceUseCase
from app.Application.usecase.derivacion.gestionar_derivacion import (
    ObtenerDerivacionUseCase, CrearDerivacionUseCase, ActualizarDerivacionUseCase,
)
from app.Application.usecase.normativa.gestionar_normativa import (
    ListarNormativaUseCase, ObtenerNormativaUseCase, CrearNormativaUseCase,
    ActualizarNormativaUseCase, EliminarNormativaUseCase,
)
from app.Application.usecase.cuadrilla.gestionar_cuadrilla import (
    ListarCuadrillasUseCase, ObtenerCuadrillaUseCase, CrearCuadrillaUseCase,
    ActualizarCuadrillaUseCase, EliminarCuadrillaUseCase,
)
from app.Application.usecase.area_comercial.gestionar_area import (
    ListarAreasUseCase, ObtenerAreaUseCase, CrearAreaUseCase,
    ActualizarAreaUseCase, EliminarAreaUseCase,
)
from app.Application.usecase.plazos.detectar_vencimiento_proximo import DetectarVencimientoProximoUseCase
from app.Application.usecase.plazos.detectar_reclamo_vencido import DetectarReclamoVencidoUseCase
from app.Application.usecase.plazos.detectar_reclamo_critico import DetectarReclamoCriticoUseCase
from app.Application.usecase.reporte.generar_reporte_diario import GenerarReporteDiarioUseCase
from app.Application.usecase.reporte.generar_reporte_mensual import GenerarReporteMensualUseCase
from app.Application.usecase.reporte.gestionar_reporte import ListarReportesUseCase, ObtenerReporteUseCase
from app.Application.usecase.reporte.obtener_dashboard import ObtenerDashboardUseCase
from app.Domain.Entities.catalogos import Rol

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

INTERNO = (Rol.tecnico, Rol.supervisor, Rol.admin)
GESTION = (Rol.supervisor, Rol.admin)
ADMIN = (Rol.admin,)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    usuario = UsuarioRepository(db).get_by_id(int(sub))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


def require_roles(*roles: Rol):
    """Dependencia que solo deja pasar a los usuarios con uno de los roles indicados."""

    async def _verificar(current_user=Depends(get_current_user)):
        if current_user.rol not in {r.value for r in roles}:
            permitidos = ", ".join(sorted(r.value for r in roles))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para esta operación. Se requiere uno de estos roles: {permitidos}",
            )
        return current_user

    return _verificar


def get_service(db: Session = Depends(get_db)):
    usuario_repo = UsuarioRepository(db)
    medidor_repo = MedidorRepository(db)
    reclamo_repo = ReclamoRepository(db)
    normativa_repo = NormativaPlazoRepository(db)
    orden_repo = OrdenTrabajoRepository(db)
    avance_repo = AvanceRepository(db)
    derivacion_repo = DerivacionComercialRepository(db)
    cuadrilla_repo = CuadrillaRepository(db)
    area_repo = AreaComercialRepository(db)
    reporte_repo = ReporteRepository(db)

    # Se inyecta en CrearUsuarioUseCase: todo cliente nace con su medidor de agua
    # y el de luz ya dados de alta.
    asignar_medidores = AsignarMedidoresPorDefectoUseCase(medidor_repo, usuario_repo)

    return {
        # Usuarios
        "listar_usuarios": ListarUsuariosUseCase(usuario_repo),
        "obtener_usuario": ObtenerUsuarioUseCase(usuario_repo),
        "crear_usuario": CrearUsuarioUseCase(usuario_repo, asignar_medidores),
        "actualizar_usuario": ActualizarUsuarioUseCase(usuario_repo),
        "eliminar_usuario": EliminarUsuarioUseCase(usuario_repo),
        "cambiar_contrasena": CambiarContrasenaUseCase(usuario_repo),
        # Medidores
        "listar_medidores": ListarMedidoresUseCase(medidor_repo),
        "obtener_medidor": ObtenerMedidorUseCase(medidor_repo),
        "listar_medidores_ciudadanos": ListarMedidoresDeCiudadanosUseCase(medidor_repo, usuario_repo),
        "crear_medidor": CrearMedidorUseCase(medidor_repo, usuario_repo),
        "actualizar_medidor": ActualizarMedidorUseCase(medidor_repo),
        "eliminar_medidor": EliminarMedidorUseCase(medidor_repo),
        # Reclamos
        "listar_reclamos": ListarReclamosUseCase(reclamo_repo),
        "obtener_reclamo": ObtenerReclamoUseCase(reclamo_repo),
        "consultar_estado_reclamo": ConsultarEstadoReclamoUseCase(reclamo_repo, usuario_repo),
        "crear_reclamo": CrearReclamoUseCase(reclamo_repo, usuario_repo, medidor_repo),
        "actualizar_reclamo": ActualizarReclamoUseCase(reclamo_repo, medidor_repo),
        "eliminar_reclamo": EliminarReclamoUseCase(reclamo_repo),
        "clasificar_reclamo": ClasificarReclamoUseCase(reclamo_repo, medidor_repo),
        "asignar_plazo": AsignarPlazoUseCase(reclamo_repo, normativa_repo),
        "resolver_reclamo": ResolverReclamoUseCase(reclamo_repo, orden_repo, avance_repo),
        "cerrar_reclamo": CerrarReclamoUseCase(reclamo_repo),
        "actualizar_contacto": ActualizarContactoUseCase(reclamo_repo, usuario_repo),
        # Normativa
        "listar_normativa": ListarNormativaUseCase(normativa_repo),
        "obtener_normativa": ObtenerNormativaUseCase(normativa_repo),
        "crear_normativa": CrearNormativaUseCase(normativa_repo),
        "actualizar_normativa": ActualizarNormativaUseCase(normativa_repo),
        "eliminar_normativa": EliminarNormativaUseCase(normativa_repo),
        # Cuadrillas
        "listar_cuadrillas": ListarCuadrillasUseCase(cuadrilla_repo, orden_repo),
        "obtener_cuadrilla": ObtenerCuadrillaUseCase(cuadrilla_repo, orden_repo),
        "crear_cuadrilla": CrearCuadrillaUseCase(cuadrilla_repo),
        "actualizar_cuadrilla": ActualizarCuadrillaUseCase(cuadrilla_repo, orden_repo),
        "eliminar_cuadrilla": EliminarCuadrillaUseCase(cuadrilla_repo),
        # Areas comerciales
        "listar_areas": ListarAreasUseCase(area_repo),
        "obtener_area": ObtenerAreaUseCase(area_repo),
        "crear_area": CrearAreaUseCase(area_repo),
        "actualizar_area": ActualizarAreaUseCase(area_repo),
        "eliminar_area": EliminarAreaUseCase(area_repo),
        # Seguimiento
        "listar_ordenes": ListarOrdenesUseCase(orden_repo),
        "obtener_orden": ObtenerOrdenUseCase(orden_repo),
        "crear_orden": CrearOrdenUseCase(orden_repo, reclamo_repo, cuadrilla_repo),
        "actualizar_orden": ActualizarOrdenUseCase(
            orden_repo, reclamo_repo, avance_repo, cuadrilla_repo
        ),
        "eliminar_orden": EliminarOrdenUseCase(orden_repo),
        "listar_avances": ListarAvancesUseCase(avance_repo),
        "crear_avance": CrearAvanceUseCase(avance_repo, orden_repo),
        "obtener_derivacion": ObtenerDerivacionUseCase(derivacion_repo),
        "crear_derivacion": CrearDerivacionUseCase(derivacion_repo, reclamo_repo),
        "actualizar_derivacion": ActualizarDerivacionUseCase(derivacion_repo, reclamo_repo),
        # Plazos
        "detectar_vencimiento_proximo": DetectarVencimientoProximoUseCase(reclamo_repo),
        "detectar_reclamo_vencido": DetectarReclamoVencidoUseCase(reclamo_repo),
        "detectar_reclamo_critico": DetectarReclamoCriticoUseCase(reclamo_repo),
        # Reportes
        "generar_reporte_diario": GenerarReporteDiarioUseCase(reclamo_repo, avance_repo, reporte_repo),
        "generar_reporte_mensual": GenerarReporteMensualUseCase(reclamo_repo, reporte_repo),
        "listar_reportes": ListarReportesUseCase(reporte_repo),
        "obtener_reporte": ObtenerReporteUseCase(reporte_repo),
        "obtener_dashboard": ObtenerDashboardUseCase(reclamo_repo, usuario_repo),
    }
