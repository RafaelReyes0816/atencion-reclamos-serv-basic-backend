from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Repositories.avance_repository import AvanceRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Domain.Entities.catalogos import EstadoReclamo
from app.Application.usecase.orden_trabajo.gestionar_orden import SIN_AVANCES
from app.Domain.Exceptions import NoEncontradoError, ConflictoError


class ResolverReclamoUseCase:
    def __init__(
        self,
        repository: ReclamoRepositoryABC,
        orden_repo: OrdenTrabajoRepositoryABC,
        avance_repo: AvanceRepositoryABC,
    ):
        self.repository = repository
        self.orden_repo = orden_repo
        self.avance_repo = avance_repo

    def execute(self, id_reclamo: int, resultado: str) -> Reclamo:
        reclamo = self.repository.get_by_id(id_reclamo)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        if reclamo.estado == EstadoReclamo.cerrado.value:
            raise ConflictoError("El reclamo ya está cerrado")
        if reclamo.estado == EstadoReclamo.registrado.value:
            raise ConflictoError("El reclamo debe ser clasificado antes de resolverse")
        # Atajo tecnico: un reclamo con orden de trabajo no se resuelve por
        # esta via sin avances. Sin orden (resolucion directa) no aplica.
        orden = self.orden_repo.get_by_reclamo(id_reclamo)
        if orden is not None and not self.avance_repo.get_by_orden(orden.id_orden):
            raise ConflictoError(SIN_AVANCES)
        reclamo.estado = EstadoReclamo.resuelto.value
        reclamo.resultado = resultado
        return self.repository.update(reclamo)


class CerrarReclamoUseCase:
    def __init__(self, repository: ReclamoRepositoryABC):
        self.repository = repository

    def execute(self, id_reclamo: int, resultado: str) -> Reclamo:
        reclamo = self.repository.get_by_id(id_reclamo)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        if reclamo.estado != EstadoReclamo.resuelto.value:
            raise ConflictoError("El reclamo debe estar en estado 'resuelto' para cerrarse")
        reclamo.estado = EstadoReclamo.cerrado.value
        reclamo.fecha_cierre = date.today()
        reclamo.resultado = resultado
        return self.repository.update(reclamo)
