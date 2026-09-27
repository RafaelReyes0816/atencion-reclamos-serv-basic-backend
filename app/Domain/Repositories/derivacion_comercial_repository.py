from abc import ABC, abstractmethod
from typing import List, Optional
from app.Domain.Entities.derivacion_comercial import DerivacionComercial


class DerivacionComercialRepositoryABC(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[DerivacionComercial]:
        ...

    @abstractmethod
    def get_by_reclamo(self, id_reclamo: int) -> Optional[DerivacionComercial]:
        ...

    @abstractmethod
    def create(self, data: dict) -> DerivacionComercial:
        ...

    @abstractmethod
    def update(self, entity: DerivacionComercial) -> DerivacionComercial:
        ...
