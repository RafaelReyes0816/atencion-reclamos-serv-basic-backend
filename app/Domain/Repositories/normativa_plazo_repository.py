from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.Domain.Entities.normativa_plazo import NormativaPlazo


class NormativaPlazoRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> List[NormativaPlazo]:
        ...

    @abstractmethod
    def get_vigente(self, servicio: str, categoria: str, urgencia: str, fecha: date) -> Optional[NormativaPlazo]:
        ...

    @abstractmethod
    def create(self, data: dict) -> NormativaPlazo:
        ...

    @abstractmethod
    def update(self, entity: NormativaPlazo) -> NormativaPlazo:
        ...
