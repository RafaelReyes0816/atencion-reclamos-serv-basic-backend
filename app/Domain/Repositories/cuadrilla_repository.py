from abc import ABC, abstractmethod
from typing import List, Optional
from app.Domain.Entities.cuadrilla import Cuadrilla


class CuadrillaRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> List[Cuadrilla]:
        ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Cuadrilla]:
        ...

    @abstractmethod
    def get_disponibles(self, especialidad: str) -> List[Cuadrilla]:
        ...

    @abstractmethod
    def create(self, data: dict) -> Cuadrilla:
        ...

    @abstractmethod
    def update(self, entity: Cuadrilla) -> Cuadrilla:
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        ...
