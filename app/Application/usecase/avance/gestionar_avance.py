from typing import List
from app.Domain.Repositories.avance_repository import AvanceRepositoryABC
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Entities.avance import Avance
from app.Domain.Entities.catalogos import EstadoOrden
from app.Domain.Exceptions import NoEncontradoError, ConflictoError


class ListarAvancesUseCase:
    def __init__(self, repository: AvanceRepositoryABC):
        self.repository = repository

    def execute(self, id_orden: int) -> List[Avance]:
        return self.repository.get_by_orden(id_orden)


class CrearAvanceUseCase:
    def __init__(self, avance_repo: AvanceRepositoryABC, orden_repo: OrdenTrabajoRepositoryABC):
        self.avance_repo = avance_repo
        self.orden_repo = orden_repo

    def execute(self, data: dict) -> Avance:
        orden = self.orden_repo.get_by_id(data["id_orden"])
        if orden is None:
            raise NoEncontradoError("Orden de trabajo no encontrada")
        if orden.estado_orden == EstadoOrden.resuelta.value:
            raise ConflictoError("No se pueden registrar avances en una orden resuelta")
        return self.avance_repo.create(dict(data))
