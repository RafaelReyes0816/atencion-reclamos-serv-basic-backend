from abc import ABC, abstractmethod
from typing import List, Optional
from app.Domain.Entities.area_comercial import AreaComercial


class AreaComercialRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> List[AreaComercial]:
        ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[AreaComercial]:
        ...

    @abstractmethod
    def create(self, data: dict) -> AreaComercial:
        ...

    @abstractmethod
    def update(self, entity: AreaComercial) -> AreaComercial:
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        ...
