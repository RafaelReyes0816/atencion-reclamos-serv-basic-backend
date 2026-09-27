from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.normativa_plazo_repository import NormativaPlazoRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Domain.Entities.catalogos import EstadoReclamo
from app.Domain.Exceptions import NoEncontradoError, ConflictoError


class AsignarPlazoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, normativa_repo: NormativaPlazoRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.normativa_repo = normativa_repo

    def execute(self, id_reclamo: int, id_normativa: int, fecha_tope: date) -> Reclamo:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        if reclamo.estado == EstadoReclamo.cerrado.value:
            raise ConflictoError("No se puede asignar plazo a un reclamo cerrado")
        if not self.normativa_repo.get_by_id(id_normativa):
            raise NoEncontradoError("Normativa no encontrada")
        reclamo.id_normativa = id_normativa
        reclamo.fecha_tope = fecha_tope
        return self.reclamo_repo.update(reclamo)
