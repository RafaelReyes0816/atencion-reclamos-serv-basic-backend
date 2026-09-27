from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.Domain.Entities.reclamo import Reclamo


class ReclamoRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> List[Reclamo]:
        ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Reclamo]:
        ...

    @abstractmethod
    def get_by_usuario(self, id_usuario: int) -> List[Reclamo]:
        ...

    @abstractmethod
    def get_by_estado(self, estado: str) -> List[Reclamo]:
        ...

    @abstractmethod
    def get_filtrados(
        self,
        estado: Optional[str] = None,
        servicio: Optional[str] = None,
        categoria: Optional[str] = None,
        urgencia: Optional[str] = None,
        canal: Optional[str] = None,
        id_usuario: Optional[int] = None,
    ) -> List[Reclamo]:
        ...

    @abstractmethod
    def get_por_vencer(self, fecha_actual: date) -> List[Reclamo]:
        ...

    @abstractmethod
    def get_vencidos(self, fecha_actual: date) -> List[Reclamo]:
        ...

    @abstractmethod
    def get_criticos(self) -> List[Reclamo]:
        ...

    @abstractmethod
    def create(self, data: dict) -> Reclamo:
        ...

    @abstractmethod
    def update(self, entity: Reclamo) -> Reclamo:
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        ...

    @abstractmethod
    def update_estado(self, id: int, estado: str) -> None:
        ...
