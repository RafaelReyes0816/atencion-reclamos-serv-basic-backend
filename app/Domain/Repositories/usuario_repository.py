from abc import ABC, abstractmethod
from typing import List, Optional
from app.Domain.Entities.usuario import Usuario


class UsuarioRepositoryABC(ABC):
    @abstractmethod
    def get_all(self) -> List[Usuario]:
        ...

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Usuario]:
        ...

    @abstractmethod
    def get_by_documento(self, documento: str) -> Optional[Usuario]:
        ...

    @abstractmethod
    def create(self, data: dict) -> Usuario:
        ...

    @abstractmethod
    def update(self, entity: Usuario) -> Usuario:
        ...
