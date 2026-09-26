from datetime import date, datetime, timedelta
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.reporte_repository import ReporteRepositoryABC
import json


class GenerarReporteMensualUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, reporte_repo: ReporteRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.reporte_repo = reporte_repo

    def execute(self) -> dict:
        fecha_actual = date.today()
        mes_anterior = fecha_actual.replace(day=1) - timedelta(days=1)
        periodo = mes_anterior.strftime("%Y-%m")

        todos = self.reclamo_repo.get_all()
        del_mes = [r for r in todos if r.fecha_recepcion.month == mes_anterior.month and r.fecha_recepcion.year == mes_anterior.year]

        total_ingresados = len(del_mes)
        total_cerrados = len([r for r in del_mes if r.estado == "cerrado"])
        total_vencidos = len([r for r in del_mes if r.fecha_tope and r.fecha_tope < fecha_actual and r.estado != "cerrado"])
        porcentaje_cumplimiento = (total_cerrados / total_ingresados * 100) if total_ingresados > 0 else 0

        contenido = json.dumps({
            "periodo": periodo,
            "total_ingresados": total_ingresados,
            "total_cerrados": total_cerrados,
            "total_vencidos": total_vencidos,
            "porcentaje_cumplimiento": round(porcentaje_cumplimiento, 2),
        })

        reporte = self.reporte_repo.create({
            "tipo_reporte": "regulatorio_mensual",
            "periodo": periodo,
            "fecha_generacion": datetime.now(),
            "contenido": contenido,
        })

        return {
            "id_reporte": reporte.id_reporte,
            "periodo": periodo,
            "total_ingresados": total_ingresados,
            "total_cerrados": total_cerrados,
            "total_vencidos": total_vencidos,
            "porcentaje_cumplimiento": round(porcentaje_cumplimiento, 2),
        }
