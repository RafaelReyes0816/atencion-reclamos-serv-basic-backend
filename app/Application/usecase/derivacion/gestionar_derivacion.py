from app.Domain.Repositories.derivacion_comercial_repository import DerivacionComercialRepositoryABC
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.derivacion_comercial import DerivacionComercial
from app.Domain.Exceptions import NoEncontradoError, ConflictoError


class ObtenerDerivacionUseCase:
    def __init__(self, repository: DerivacionComercialRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> DerivacionComercial:
        derivacion = self.repository.get_by_id(id)
        if derivacion is None:
            raise NoEncontradoError("Derivación no encontrada")
        return derivacion

    def execute_por_reclamo(self, id_reclamo: int) -> DerivacionComercial:
        derivacion = self.repository.get_by_reclamo(id_reclamo)
        if derivacion is None:
            raise NoEncontradoError("No hay derivación para este reclamo")
        return derivacion


class CrearDerivacionUseCase:
    def __init__(self, derivacion_repo: DerivacionComercialRepositoryABC, reclamo_repo: ReclamoRepositoryABC):
        self.derivacion_repo = derivacion_repo
        self.reclamo_repo = reclamo_repo

    def execute(self, data: dict) -> DerivacionComercial:
        if not self.reclamo_repo.get_by_id(data["id_reclamo"]):
            raise NoEncontradoError("Reclamo no encontrado")
        if self.derivacion_repo.get_by_reclamo(data["id_reclamo"]):
            raise ConflictoError("El reclamo ya tiene una derivación comercial")
        data = dict(data)
        data["estado_derivacion"] = "derivada"
        return self.derivacion_repo.create(data)


class ActualizarDerivacionUseCase:
    def __init__(self, repository: DerivacionComercialRepositoryABC):
        self.repository = repository

    def execute(self, id: int, cambios: dict) -> DerivacionComercial:
        derivacion = self.repository.get_by_id(id)
        if derivacion is None:
            raise NoEncontradoError("Derivación no encontrada")
        for campo, valor in cambios.items():
            if valor is not None and hasattr(derivacion, campo):
                setattr(derivacion, campo, valor)
        return self.repository.update(derivacion)
