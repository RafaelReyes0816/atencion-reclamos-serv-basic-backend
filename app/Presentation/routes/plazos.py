from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.Infraestructura.database import get_db
from app.Infraestructura.repositories.reclamo_repository import ReclamoRepository
from app.Presentation.dependencies import get_current_user
from datetime import date, timedelta

router = APIRouter(prefix="/plazos", tags=["plazos"])


@router.post("/verificar-vencimientos")
def verificar_vencimientos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    fecha_actual = date.today()
    reclamos = repo.get_por_vencer(fecha_actual)
    umbral = 0.2
    avisos = []
    for reclamo in reclamos:
        if reclamo.fecha_tope:
            dias_restantes = (reclamo.fecha_tope - fecha_actual).days
            plazo_total = (reclamo.fecha_tope - reclamo.fecha_recepcion).days
            if plazo_total > 0 and dias_restantes <= plazo_total * umbral:
                avisos.append({
                    "id_reclamo": reclamo.id_reclamo,
                    "fecha_tope": reclamo.fecha_tope,
                    "dias_restantes": dias_restantes,
                })
    return {"avisos": avisos, "total": len(avisos)}


@router.post("/verificar-vencidos")
def verificar_vencidos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    fecha_actual = date.today()
    reclamos = repo.get_vencidos(fecha_actual)
    alertas = []
    for reclamo in reclamos:
        if reclamo.fecha_tope:
            exceso_dias = (fecha_actual - reclamo.fecha_tope).days
            alertas.append({
                "id_reclamo": reclamo.id_reclamo,
                "fecha_tope": reclamo.fecha_tope,
                "exceso_dias": exceso_dias,
            })
            repo.update_estado(reclamo.id_reclamo, "escalado")
    return {"alertas": alertas, "total": len(alertas)}


@router.post("/verificar-criticos")
def verificar_criticos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = ReclamoRepository(db)
    reclamos = repo.get_criticos()
    alarmas = []
    for reclamo in reclamos:
        alarmas.append({
            "id_reclamo": reclamo.id_reclamo,
            "servicio": reclamo.servicio,
            "categoria": reclamo.categoria,
            "urgencia": reclamo.urgencia,
        })
    return {"alarmas": alarmas, "total": len(alarmas)}
