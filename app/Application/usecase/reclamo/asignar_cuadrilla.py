from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Repositories.cuadrilla_repository import CuadrillaRepositoryABC
from app.Domain.Entities.catalogos import EstadoReclamo, EstadoOrden


class AsignarCuadrillaUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, orden_repo: OrdenTrabajoRepositoryABC, cuadrilla_repo: CuadrillaRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.orden_repo = orden_repo
        self.cuadrilla_repo = cuadrilla_repo

    def execute(self, id_reclamo: int) -> dict:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if not reclamo:
            raise ValueError("Reclamo no encontrado")

        cuadrillas = self.cuadrilla_repo.get_disponibles(reclamo.servicio)
        if not cuadrillas:
            raise ValueError("No hay cuadrillas disponibles para este servicio")

        cuadrilla = cuadrillas[0]

        orden = self.orden_repo.create({
            "id_reclamo": id_reclamo,
            "cuadrilla": cuadrilla.nombre,
            "fecha_asignacion": date.today(),
            "estado_orden": EstadoOrden.asignada.value,
        })

        reclamo.estado = EstadoReclamo.en_atencion_tecnica.value
        self.reclamo_repo.update(reclamo)

        return {
            "id_orden": orden.id_orden,
            "cuadrilla": cuadrilla.nombre,
            "estado_reclamo": reclamo.estado,
        }
