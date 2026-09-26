from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Repositories.avance_repository import AvanceRepositoryABC
from app.Domain.Entities.catalogos import EstadoOrden


class RegistrarAvanceUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, orden_repo: OrdenTrabajoRepositoryABC, avance_repo: AvanceRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.orden_repo = orden_repo
        self.avance_repo = avance_repo

    def execute(self, id_orden: int, fecha_avance: str, descripcion: str, estado_parcial: str) -> dict:
        orden = self.orden_repo.get_by_id(id_orden)
        if not orden:
            raise ValueError("Orden no encontrada")
        if orden.estado_orden not in [EstadoOrden.asignada.value, EstadoOrden.en_curso.value]:
            raise ValueError("La orden no permite avances en su estado actual")

        avance = self.avance_repo.create({
            "id_orden": id_orden,
            "fecha_avance": fecha_avance,
            "descripcion": descripcion,
            "estado_parcial": estado_parcial,
        })

        orden.estado_orden = EstadoOrden.en_curso.value
        self.orden_repo.update(orden)

        return {
            "id_avance": avance.id_avance,
            "estado_orden": orden.estado_orden,
        }
