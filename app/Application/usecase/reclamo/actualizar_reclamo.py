from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Domain.Entities.catalogos import EstadoReclamo
from app.Domain.Exceptions import NoEncontradoError, ConflictoError


class ActualizarReclamoUseCase:
    def __init__(self, repository: ReclamoRepositoryABC):
        self.repository = repository

    def execute(self, id: int, cambios: dict) -> Reclamo:
        reclamo = self.repository.get_by_id(id)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        if reclamo.estado == EstadoReclamo.cerrado.value:
            raise ConflictoError("No se puede modificar un reclamo cerrado")
        for campo, valor in cambios.items():
            if valor is not None and hasattr(reclamo, campo):
                setattr(reclamo, campo, valor)
        return self.repository.update(reclamo)


class EliminarReclamoUseCase:
    def __init__(self, repository: ReclamoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            raise NoEncontradoError(str(e))
