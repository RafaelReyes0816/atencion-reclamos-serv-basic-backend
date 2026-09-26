from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC


class DetectarReclamoCriticoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC):
        self.reclamo_repo = reclamo_repo

    def execute(self) -> list:
        reclamos = self.reclamo_repo.get_criticos()
        alarmas = []
        for reclamo in reclamos:
            alarmas.append({
                "id_reclamo": reclamo.id_reclamo,
                "servicio": reclamo.servicio,
                "categoria": reclamo.categoria,
                "urgencia": reclamo.urgencia,
            })
        return alarmas
