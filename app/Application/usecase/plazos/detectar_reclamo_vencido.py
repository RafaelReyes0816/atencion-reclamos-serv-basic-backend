from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Entities.catalogos import EstadoReclamo


class DetectarReclamoVencidoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC):
        self.reclamo_repo = reclamo_repo

    def execute(self) -> list:
        fecha_actual = date.today()
        reclamos = self.reclamo_repo.get_vencidos(fecha_actual)
        alertas = []
        for reclamo in reclamos:
            if reclamo.fecha_tope:
                exceso_dias = (fecha_actual - reclamo.fecha_tope).days
                alertas.append({
                    "id_reclamo": reclamo.id_reclamo,
                    "fecha_tope": reclamo.fecha_tope,
                    "exceso_dias": exceso_dias,
                })
                reclamo.estado = EstadoReclamo.escalado.value
                self.reclamo_repo.update(reclamo)
        return alertas
