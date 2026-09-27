from fastapi import APIRouter, Depends
from app.Presentation.dependencies import require_roles, get_service, GESTION

router = APIRouter(prefix="/plazos", tags=["plazos"])


@router.post("/verificar-vencimientos")
def verificar_vencimientos(
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    avisos = use_cases["detectar_vencimiento_proximo"].execute()
    return {"avisos": avisos, "total": len(avisos)}


@router.post("/verificar-vencidos")
def verificar_vencidos(
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    alertas = use_cases["detectar_reclamo_vencido"].execute()
    return {"alertas": alertas, "total": len(alertas)}


@router.post("/verificar-criticos")
def verificar_criticos(
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    alarmas = use_cases["detectar_reclamo_critico"].execute()
    return {"alarmas": alarmas, "total": len(alarmas)}
