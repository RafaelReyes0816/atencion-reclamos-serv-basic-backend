from datetime import date, datetime, timedelta
from app.Domain.Exceptions import ValidacionError
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.reporte_repository import ReporteRepositoryABC
import json
import re

FORMATO_PERIODO = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class GenerarReporteMensualUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, reporte_repo: ReporteRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.reporte_repo = reporte_repo

    def execute(self, periodo: str | None = None) -> dict:
        """Genera el reporte regulatorio de un mes.

        Sin `periodo` usa el mes anterior, que es lo que corresponde a un
        periodo ya cerrado y lo que reporta el job programado el dia 1. Con
        `periodo` ("AAAA-MM") se puede pedir cualquier mes, útil para
        consultar el mes en curso o reprocesar uno anterior.
        """
        fecha_actual = date.today()

        if periodo is None:
            referencia = fecha_actual.replace(day=1) - timedelta(days=1)
            anio, mes = referencia.year, referencia.month
        else:
            if not FORMATO_PERIODO.match(periodo):
                raise ValidacionError(
                    f"El periodo '{periodo}' no es valido. Use el formato AAAA-MM, por ejemplo 2026-09."
                )
            anio, mes = int(periodo[:4]), int(periodo[5:7])

        periodo_final = f"{anio:04d}-{mes:02d}"

        todos = self.reclamo_repo.get_all()
        del_mes = [
            r for r in todos
            if r.fecha_recepcion.year == anio and r.fecha_recepcion.month == mes
        ]

        total_ingresados = len(del_mes)
        total_cerrados = len([r for r in del_mes if r.estado == "cerrado"])
        total_vencidos = len([r for r in del_mes if r.fecha_tope and r.fecha_tope < fecha_actual and r.estado != "cerrado"])
        porcentaje_cumplimiento = (total_cerrados / total_ingresados * 100) if total_ingresados > 0 else 0

        contenido = json.dumps({
            "periodo": periodo_final,
            "total_ingresados": total_ingresados,
            "total_cerrados": total_cerrados,
            "total_vencidos": total_vencidos,
            "porcentaje_cumplimiento": round(porcentaje_cumplimiento, 2),
        })

        reporte = self.reporte_repo.create({
            "tipo_reporte": "regulatorio_mensual",
            "periodo": periodo_final,
            "fecha_generacion": datetime.now(),
            "contenido": contenido,
        })

        return {
            "id_reporte": reporte.id_reporte,
            "periodo": periodo_final,
            "total_ingresados": total_ingresados,
            "total_cerrados": total_cerrados,
            "total_vencidos": total_vencidos,
            "porcentaje_cumplimiento": round(porcentaje_cumplimiento, 2),
        }
