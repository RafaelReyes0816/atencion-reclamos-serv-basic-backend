from typing import List
from app.Domain.Repositories.cuadrilla_repository import CuadrillaRepositoryABC
from app.Domain.Entities.cuadrilla import Cuadrilla
from app.Domain.Exceptions import NoEncontradoError


class ListarCuadrillasUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC):
        self.repository = repository

    def execute(self) -> List[Cuadrilla]:
        return self.repository.get_all()

    def execute_disponibles(self, especialidad: str) -> List[Cuadrilla]:
        return self.repository.get_disponibles(especialidad)


class ObtenerCuadrillaUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> Cuadrilla:
        cuadrilla = self.repository.get_by_id(id)
        if cuadrilla is None:
            raise NoEncontradoError("Cuadrilla no encontrada")
        return cuadrilla


class CrearCuadrillaUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC):
        self.repository = repository

    def execute(self, data: dict) -> Cuadrilla:
        return self.repository.create(dict(data))


class ActualizarCuadrillaUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC):
        self.repository = repository

    def execute(self, id: int, cambios: dict) -> Cuadrilla:
        cuadrilla = self.repository.get_by_id(id)
        if cuadrilla is None:
            raise NoEncontradoError("Cuadrilla no encontrada")
        for campo, valor in cambios.items():
            if valor is not None and hasattr(cuadrilla, campo):
                setattr(cuadrilla, campo, valor)
        return self.repository.update(cuadrilla)


class EliminarCuadrillaUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            raise NoEncontradoError(str(e))
