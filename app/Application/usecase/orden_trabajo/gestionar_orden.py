from typing import List
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Entities.orden_trabajo import OrdenTrabajo
from app.Domain.Exceptions import NoEncontradoError, ConflictoError


class ListarOrdenesUseCase:
    def __init__(self, repository: OrdenTrabajoRepositoryABC):
        self.repository = repository

    def execute(self) -> List[OrdenTrabajo]:
        return self.repository.get_all()


class ObtenerOrdenUseCase:
    def __init__(self, repository: OrdenTrabajoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> OrdenTrabajo:
        orden = self.repository.get_by_id(id)
        if orden is None:
            raise NoEncontradoError("Orden no encontrada")
        return orden

    def execute_por_reclamo(self, id_reclamo: int) -> OrdenTrabajo:
        orden = self.repository.get_by_reclamo(id_reclamo)
        if orden is None:
            raise NoEncontradoError("No hay orden para este reclamo")
        return orden


class CrearOrdenUseCase:
    def __init__(self, orden_repo: OrdenTrabajoRepositoryABC, reclamo_repo):
        self.orden_repo = orden_repo
        self.reclamo_repo = reclamo_repo

    def execute(self, data: dict) -> OrdenTrabajo:
        reclamo = self.reclamo_repo.get_by_id(data["id_reclamo"])
        if not reclamo:
            raise NoEncontradoError("Reclamo no encontrado")
        if self.orden_repo.get_by_reclamo(data["id_reclamo"]):
            raise ConflictoError("El reclamo ya tiene una orden de trabajo")
        data = dict(data)
        data["estado_orden"] = "asignada"
        orden = self.orden_repo.create(data)
        self.reclamo_repo.update_estado(reclamo.id_reclamo, "en_atencion_tecnica")
        return orden


class ActualizarOrdenUseCase:
    def __init__(self, repository: OrdenTrabajoRepositoryABC, reclamo_repo=None):
        self.repository = repository
        self.reclamo_repo = reclamo_repo

    def execute(self, id: int, cambios: dict) -> OrdenTrabajo:
        orden = self.repository.get_by_id(id)
        if orden is None:
            raise NoEncontradoError("Orden no encontrada")
        for campo, valor in cambios.items():
            if valor is not None and hasattr(orden, campo):
                setattr(orden, campo, valor)
        resultado = self.repository.update(orden)
        if (
            self.reclamo_repo
            and cambios.get("estado_orden") == "resuelta"
            and orden.id_reclamo
        ):
            self.reclamo_repo.update_estado(orden.id_reclamo, "resuelto")
        return resultado


class EliminarOrdenUseCase:
    def __init__(self, repository: OrdenTrabajoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            raise NoEncontradoError(str(e))
