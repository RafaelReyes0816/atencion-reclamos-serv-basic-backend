from abc import ABC, abstractmethod
from typing import List, Optional
from app.Domain.Entities.avance import Avance


class AvanceRepositoryABC(ABC):
    @abstractmethod
    def get_by_orden(self, id_orden: int) -> List[Avance]:
        ...

    @abstractmethod
    def create(self, data: dict) -> Avance:
        ...
