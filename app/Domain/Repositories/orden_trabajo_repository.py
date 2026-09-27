from abc import ABC, abstractmethod
from typing import List, Optional
from app.Domain.Entities.orden_trabajo import OrdenTrabajo


class OrdenTrabajoRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> List[OrdenTrabajo]:
        ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[OrdenTrabajo]:
        ...

    @abstractmethod
    def get_by_reclamo(self, id_reclamo: int) -> Optional[OrdenTrabajo]:
        ...

    @abstractmethod
    def create(self, data: dict) -> OrdenTrabajo:
        ...

    @abstractmethod
    def update(self, entity: OrdenTrabajo) -> OrdenTrabajo:
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        ...
