from typing import List
from datetime import date
from app.Domain.Repositories.normativa_plazo_repository import NormativaPlazoRepositoryABC
from app.Domain.Entities.normativa_plazo import NormativaPlazo
from app.Domain.Exceptions import NoEncontradoError


class ListarNormativaUseCase:
    def __init__(self, repository: NormativaPlazoRepositoryABC):
        self.repository = repository

    def execute(self, **filtros) -> List[NormativaPlazo]:
        return self.repository.get_filtrados(**filtros)


class ObtenerNormativaUseCase:
    def __init__(self, repository: NormativaPlazoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> NormativaPlazo:
        normativa = self.repository.get_by_id(id)
        if normativa is None:
            raise NoEncontradoError("Normativa no encontrada")
        return normativa

    def execute_vigente(self, servicio: str, categoria: str, urgencia: str) -> NormativaPlazo:
        normativa = self.repository.get_vigente(servicio, categoria, urgencia, date.today())
        if normativa is None:
            raise NoEncontradoError("No hay normativa vigente para esta combinación")
        return normativa


class CrearNormativaUseCase:
    def __init__(self, repository: NormativaPlazoRepositoryABC):
        self.repository = repository

    def execute(self, data: dict) -> NormativaPlazo:
        return self.repository.create(dict(data))


class ActualizarNormativaUseCase:
    def __init__(self, repository: NormativaPlazoRepositoryABC):
        self.repository = repository

    def execute(self, id: int, cambios: dict) -> NormativaPlazo:
        normativa = self.repository.get_by_id(id)
        if normativa is None:
            raise NoEncontradoError("Normativa no encontrada")
        for campo, valor in cambios.items():
            if valor is not None and hasattr(normativa, campo):
                setattr(normativa, campo, valor)
        return self.repository.update(normativa)


class EliminarNormativaUseCase:
    def __init__(self, repository: NormativaPlazoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            raise NoEncontradoError(str(e))
