from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.repositories.reclamo_repository import ReclamoRepository
from app.Infraestructura.repositories.reporte_repository import ReporteRepository
from app.Presentation.dependencies import get_current_user
from datetime import date, datetime
import json

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/")
def listar_reportes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReporteRepository(db)
    return repo.get_all()


@router.post("/diario")
def generar_reporte_diario(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    reclamo_repo = ReclamoRepository(db)
    reporte_repo = ReporteRepository(db)

    fecha_actual = date.today()
    todos = reclamo_repo.get_all()

    ingresados = len([r for r in todos if r.fecha_recepcion == fecha_actual])
    en_atencion = len([r for r in todos if r.estado in ["en_atencion_tecnica", "en_atencion_comercial"]])
    proximos_vencer = len(reclamo_repo.get_por_vencer(fecha_actual))
    vencidos = len(reclamo_repo.get_vencidos(fecha_actual))
    criticos = len(reclamo_repo.get_criticos())

    contenido = json.dumps({
        "fecha": fecha_actual.isoformat(),
        "ingresados": ingresados,
        "en_atencion": en_atencion,
        "proximos_vencer": proximos_vencer,
        "vencidos": vencidos,
        "criticos": criticos,
    })

    reporte = reporte_repo.create({
        "tipo_reporte": "operativo_diario",
        "periodo": fecha_actual.isoformat(),
        "fecha_generacion": datetime.now(),
        "contenido": contenido,
    })

    return {"message": "Reporte diario generado", "id_reporte": reporte.id_reporte}


@router.post("/mensual")
def generar_reporte_mensual(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    reclamo_repo = ReclamoRepository(db)
    reporte_repo = ReporteRepository(db)

    fecha_actual = date.today()
    mes_anterior = fecha_actual.replace(day=1) - timedelta(days=1)
    periodo = mes_anterior.strftime("%Y-%m")

    todos = reclamo_repo.get_all()
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

    reporte = reporte_repo.create({
        "tipo_reporte": "regulatorio_mensual",
        "periodo": periodo,
        "fecha_generacion": datetime.now(),
        "contenido": contenido,
    })

    return {"message": "Reporte mensual generado", "id_reporte": reporte.id_reporte}
