from abc import ABC, abstractmethod
from typing import List, Optional

from app.Domain.Entities.medidor import Medidor


class MedidorRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> List[Medidor]: ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Medidor]: ...

    @abstractmethod
    def get_by_usuario(self, id_usuario: int) -> List[Medidor]: ...

    @abstractmethod
    def get_por_servicio(self, id_usuario: int, servicio: str) -> Optional[Medidor]: ...

    @abstractmethod
    def get_by_numero(self, numero: str) -> Optional[Medidor]: ...

    @abstractmethod
    def create(self, data: dict) -> Medidor: ...

    @abstractmethod
    def update(self, entity: Medidor) -> Medidor: ...

    @abstractmethod
    def delete(self, id: int) -> None: ...
