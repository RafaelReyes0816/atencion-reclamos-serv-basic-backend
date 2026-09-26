from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.catalogos import EstadoReclamo


class ResolverReclamoComercialUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC):
        self.reclamo_repo = reclamo_repo

    def execute(self, id_reclamo: int, resultado: str) -> dict:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if not reclamo:
            raise ValueError("Reclamo no encontrado")
        if reclamo.estado != EstadoReclamo.en_atencion_comercial.value:
            raise ValueError("El reclamo no está en atención comercial")

        reclamo.estado = EstadoReclamo.resuelto.value
        reclamo.resultado = resultado
        self.reclamo_repo.update(reclamo)

        return {
            "id_reclamo": reclamo.id_reclamo,
            "estado": reclamo.estado,
            "resultado": reclamo.resultado,
        }
