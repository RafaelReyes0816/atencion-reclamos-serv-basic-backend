import json
from typing import List
from app.Domain.Repositories.reporte_repository import ReporteRepositoryABC
from app.Domain.Entities.reporte import Reporte
from app.Domain.Exceptions import NoEncontradoError


class ListarReportesUseCase:
    def __init__(self, repository: ReporteRepositoryABC):
        self.repository = repository

    def execute(self) -> List[Reporte]:
        return self.repository.get_all()


class ObtenerReporteUseCase:
    def __init__(self, repository: ReporteRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> Reporte:
        reporte = self.repository.get_by_id(id)
        if reporte is None:
            raise NoEncontradoError("Reporte no encontrado")
        return reporte

    @staticmethod
    def parsear_contenido(reporte: Reporte) -> dict:
        try:
            return json.loads(reporte.contenido)
        except (json.JSONDecodeError, TypeError):
            return {"contenido_raw": reporte.contenido}
