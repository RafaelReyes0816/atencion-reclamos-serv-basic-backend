from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.avance_repository import AvanceRepositoryABC
from app.Domain.Repositories.reporte_repository import ReporteRepositoryABC
import json


class GenerarReporteDiarioUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, avance_repo: AvanceRepositoryABC, reporte_repo: ReporteRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.avance_repo = avance_repo
        self.reporte_repo = reporte_repo

    def execute(self) -> dict:
        fecha_actual = date.today()
        todos = self.reclamo_repo.get_all()

        ingresados = len([r for r in todos if r.fecha_recepcion == fecha_actual])
        en_atencion = len([r for r in todos if r.estado in ["en_atencion_tecnica", "en_atencion_comercial"]])
        proximos_vencer = len(self.reclamo_repo.get_por_vencer(fecha_actual))
        vencidos = len(self.reclamo_repo.get_vencidos(fecha_actual))
        criticos = len(self.reclamo_repo.get_criticos())

        contenido = json.dumps({
            "fecha": fecha_actual.isoformat(),
            "ingresados": ingresados,
            "en_atencion": en_atencion,
            "proximos_vencer": proximos_vencer,
            "vencidos": vencidos,
            "criticos": criticos,
        })

        from datetime import datetime
        reporte = self.reporte_repo.create({
            "tipo_reporte": "operativo_diario",
            "periodo": fecha_actual.isoformat(),
            "fecha_generacion": datetime.now(),
            "contenido": contenido,
        })

        return {
            "id_reporte": reporte.id_reporte,
            "fecha": fecha_actual.isoformat(),
            "ingresados": ingresados,
            "en_atencion": en_atencion,
            "proximos_vencer": proximos_vencer,
            "vencidos": vencidos,
            "criticos": criticos,
        }
