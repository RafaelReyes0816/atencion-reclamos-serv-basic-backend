from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Domain.Entities.catalogos import EstadoReclamo
from app.Domain.Exceptions import NoEncontradoError, ConflictoError


class ResolverReclamoUseCase:
    def __init__(self, repository: ReclamoRepositoryABC):
        self.repository = repository

    def execute(self, id_reclamo: int, resultado: str) -> Reclamo:
        reclamo = self.repository.get_by_id(id_reclamo)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        if reclamo.estado == EstadoReclamo.cerrado.value:
            raise ConflictoError("El reclamo ya está cerrado")
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
