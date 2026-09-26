from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.catalogos import EstadoReclamo


class CerrarReclamoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC):
        self.reclamo_repo = reclamo_repo

    def execute(self, id_reclamo: int, resultado: str) -> dict:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if not reclamo:
            raise ValueError("Reclamo no encontrado")
        if reclamo.estado != EstadoReclamo.resuelto.value:
            raise ValueError("El reclamo debe estar resuelto para cerrarse")

        reclamo.estado = EstadoReclamo.cerrado.value
        reclamo.fecha_cierre = date.today()
        reclamo.resultado = resultado
        self.reclamo_repo.update(reclamo)

        return {
            "id_reclamo": reclamo.id_reclamo,
            "estado": reclamo.estado,
            "fecha_cierre": reclamo.fecha_cierre,
            "resultado": reclamo.resultado,
        }
