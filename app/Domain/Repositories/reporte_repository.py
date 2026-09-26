from abc import ABC, abstractmethod
from typing import List, Optional
from app.Domain.Entities.reporte import Reporte


class ReporteRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> List[Reporte]:
        ...

    @abstractmethod
    def get_by_tipo(self, tipo: str) -> List[Reporte]:
        ...

    @abstractmethod
    def create(self, data: dict) -> Reporte:
        ...
