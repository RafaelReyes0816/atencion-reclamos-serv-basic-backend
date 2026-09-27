from typing import List
from app.Domain.Repositories.area_comercial_repository import AreaComercialRepositoryABC
from app.Domain.Entities.area_comercial import AreaComercial
from app.Domain.Exceptions import NoEncontradoError


class ListarAreasUseCase:
    def __init__(self, repository: AreaComercialRepositoryABC):
        self.repository = repository

    def execute(self) -> List[AreaComercial]:
        return self.repository.get_all()


class ObtenerAreaUseCase:
    def __init__(self, repository: AreaComercialRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> AreaComercial:
        area = self.repository.get_by_id(id)
        if area is None:
            raise NoEncontradoError("Área comercial no encontrada")
        return area


class CrearAreaUseCase:
    def __init__(self, repository: AreaComercialRepositoryABC):
        self.repository = repository

    def execute(self, data: dict) -> AreaComercial:
        return self.repository.create(dict(data))


class ActualizarAreaUseCase:
    def __init__(self, repository: AreaComercialRepositoryABC):
        self.repository = repository

    def execute(self, id: int, cambios: dict) -> AreaComercial:
        area = self.repository.get_by_id(id)
        if area is None:
            raise NoEncontradoError("Área comercial no encontrada")
        for campo, valor in cambios.items():
            if valor is not None and hasattr(area, campo):
                setattr(area, campo, valor)
        return self.repository.update(area)


class EliminarAreaUseCase:
    def __init__(self, repository: AreaComercialRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            raise NoEncontradoError(str(e))
