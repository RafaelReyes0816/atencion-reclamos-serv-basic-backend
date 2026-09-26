from datetime import date, timedelta
from app.Domain.Repositories.normativa_plazo_repository import NormativaPlazoRepositoryABC
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC


class AsignarPlazoUseCase:
    def __init__(self, normativa_repo: NormativaPlazoRepositoryABC, reclamo_repo: ReclamoRepositoryABC):
        self.normativa_repo = normativa_repo
        self.reclamo_repo = reclamo_repo

    def execute(self, id_reclamo: int, servicio: str, categoria: str, urgencia: str) -> dict:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if not reclamo:
            raise ValueError("Reclamo no encontrado")

        normativa = self.normativa_repo.get_vigente(servicio, categoria, urgencia, reclamo.fecha_recepcion)
        if not normativa:
            plazo_default = 30
            fecha_tope = reclamo.fecha_recepcion + timedelta(days=plazo_default)
        else:
            fecha_tope = reclamo.fecha_recepcion + timedelta(days=normativa.plazo_maximo_dias)
            reclamo.id_normativa = normativa.id_normativa

        reclamo.fecha_tope = fecha_tope
        self.reclamo_repo.update(reclamo)

        return {
            "id_reclamo": reclamo.id_reclamo,
            "fecha_tope": fecha_tope,
            "id_normativa": reclamo.id_normativa,
        }
