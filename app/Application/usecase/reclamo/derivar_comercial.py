from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.derivacion_comercial_repository import DerivacionComercialRepositoryABC
from app.Domain.Entities.catalogos import EstadoReclamo


class DerivarComercialUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, derivacion_repo: DerivacionComercialRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.derivacion_repo = derivacion_repo

    def execute(self, id_reclamo: int, area_comercial: str) -> dict:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if not reclamo:
            raise ValueError("Reclamo no encontrado")

        derivacion = self.derivacion_repo.create({
            "id_reclamo": id_reclamo,
            "fecha_derivacion": date.today(),
            "area_comercial": area_comercial,
            "estado_derivacion": "derivada",
        })

        reclamo.estado = EstadoReclamo.en_atencion_comercial.value
        self.reclamo_repo.update(reclamo)

        return {
            "id_derivacion": derivacion.id_derivacion,
            "area_comercial": area_comercial,
            "estado_reclamo": reclamo.estado,
        }
