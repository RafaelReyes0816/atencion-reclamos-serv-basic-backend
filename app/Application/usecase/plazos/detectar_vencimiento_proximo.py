from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC


class DetectarVencimientoProximoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC):
        self.reclamo_repo = reclamo_repo

    def execute(self, umbral_porcentaje: float = 0.2) -> list:
        fecha_actual = date.today()
        reclamos = self.reclamo_repo.get_por_vencer(fecha_actual)
        avisos = []
        for reclamo in reclamos:
            if reclamo.fecha_tope:
                dias_restantes = (reclamo.fecha_tope - fecha_actual).days
                plazo_total = (reclamo.fecha_tope - reclamo.fecha_recepcion).days
                if plazo_total > 0 and dias_restantes <= plazo_total * umbral_porcentaje:
                    avisos.append({
                        "id_reclamo": reclamo.id_reclamo,
                        "fecha_tope": reclamo.fecha_tope,
                        "dias_restantes": dias_restantes,
                    })
        return avisos
