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
    def contar_activas_por_cuadrilla(self, excluir_id_orden: int | None = None) -> dict:
        """Ordenes activas por cuadrilla, indexadas por id_cuadrilla.

        Solo cuentan las ordenes que siguen en curso (`asignada`, `en_curso`):
        al pasar a `resuelta` la cuadrilla recupera el cupo solo, sin ninguna
        tarea programada. Las ordenes sin cuadrilla (id en NULL) no aparecen
        porque no consumen cupo de nadie.

        `excluir_id_orden` deja fuera una orden del conteo, lo que permite
        reasignar una orden sin que esta se bloquee a si misma.
        """
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
