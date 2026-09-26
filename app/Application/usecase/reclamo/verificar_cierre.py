from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.avance_repository import AvanceRepositoryABC
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Entities.catalogos import EstadoReclamo, EstadoOrden


class VerificarCierreUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, avance_repo: AvanceRepositoryABC, orden_repo: OrdenTrabajoRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.avance_repo = avance_repo
        self.orden_repo = orden_repo

    def execute(self, id_reclamo: int) -> dict:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if not reclamo:
            raise ValueError("Reclamo no encontrado")
        if reclamo.estado != EstadoReclamo.resuelto.value:
            return {"apto": False, "motivo": "El reclamo no está resuelto"}

        orden = self.orden_repo.get_by_reclamo(id_reclamo)
        if orden:
            if orden.estado_orden != EstadoOrden.resuelta.value:
                return {"apto": False, "motivo": "La orden técnica no está resuelta"}
            avances = self.avance_repo.get_by_orden(orden.id_orden)
            if not avances:
                return {"apto": False, "motivo": "No hay avances registrados"}

        return {"apto": True, "motivo": ""}
