from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Entities.catalogos import EstadoReclamo, EstadoOrden


class ResolverReclamoTecnicoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, orden_repo: OrdenTrabajoRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.orden_repo = orden_repo

    def execute(self, id_reclamo: int, resultado: str) -> dict:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if not reclamo:
            raise ValueError("Reclamo no encontrado")

        orden = self.orden_repo.get_by_reclamo(id_reclamo)
        if orden:
            orden.estado_orden = EstadoOrden.resuelta.value
            self.orden_repo.update(orden)

        reclamo.estado = EstadoReclamo.resuelto.value
        reclamo.resultado = resultado
        self.reclamo_repo.update(reclamo)

        return {
            "id_reclamo": reclamo.id_reclamo,
            "estado": reclamo.estado,
            "resultado": reclamo.resultado,
        }
