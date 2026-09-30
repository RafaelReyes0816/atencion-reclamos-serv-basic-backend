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
    def get_by_id_con_bloqueo(self, id: int) -> Optional[Cuadrilla]:
        """Igual que get_by_id, pero bloquea la fila hasta el commit.

        Se usa antes de validar la capacidad: sin el bloqueo, dos supervisores
        que asignan a la vez pueden leer el mismo conteo y los dos pasar el
        control, dejando la cuadrilla por encima de su tope. El bloqueo
        serializa esas asignaciones. En SQLite el motor no implementa
        SELECT ... FOR UPDATE, asi que ahi el no-op es inocuo.
        """
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
