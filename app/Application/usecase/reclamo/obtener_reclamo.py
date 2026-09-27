from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Domain.Entities.catalogos import EstadoReclamo
from app.Domain.Exceptions import NoEncontradoError, ConflictoError

_ESTADOS_BLOQUEADOS = (EstadoReclamo.cerrado.value, EstadoReclamo.resuelto.value)


class ObtenerReclamoUseCase:
    def __init__(self, repository: ReclamoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> Reclamo:
        reclamo = self.repository.get_by_id(id)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        return reclamo

    def execute_por_usuario(self, id_usuario: int) -> Reclamo:
        reclamos = self.repository.get_by_usuario(id_usuario)
        if not reclamos:
            raise NoEncontradoError("El usuario no tiene reclamos registrados")
        return reclamos[0]


class ConsultarEstadoReclamoUseCase:
    """Consulta publica de seguimiento: acepta el id del reclamo o el documento del usuario."""

    def __init__(self, reclamo_repo: ReclamoRepositoryABC, usuario_repo: UsuarioRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.usuario_repo = usuario_repo

    def execute(self, id_o_documento: str) -> Reclamo:
        reclamo = None
        if id_o_documento.isdigit():
            reclamo = self.reclamo_repo.get_by_id(int(id_o_documento))
        if reclamo is None:
            usuario = self.usuario_repo.get_by_documento(id_o_documento)
            if usuario is None:
                raise NoEncontradoError("No encontrado")
            reclamos = self.reclamo_repo.get_by_usuario(usuario.id_usuario)
            if not reclamos:
                raise NoEncontradoError("El usuario no tiene reclamos registrados")
            reclamo = reclamos[0]
        return reclamo


class ClasificarReclamoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC):
        self.reclamo_repo = reclamo_repo

    def execute(self, id_reclamo: int, servicio: str, categoria: str, urgencia: str) -> Reclamo:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        if reclamo.estado in _ESTADOS_BLOQUEADOS:
            raise ConflictoError("No se puede clasificar un reclamo resuelto o cerrado")
        reclamo.servicio = servicio
        reclamo.categoria = categoria
        reclamo.urgencia = urgencia
        reclamo.estado = EstadoReclamo.clasificado.value
        return self.reclamo_repo.update(reclamo)
