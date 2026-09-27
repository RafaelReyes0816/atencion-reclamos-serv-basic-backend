from fastapi import APIRouter, Depends
from app.Presentation.schemas.dashboard import DashboardResponse
from app.Presentation.dependencies import require_roles, get_service, GESTION

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
def obtener_dashboard(
    use_cases=Depends(get_service),
    current_user=Depends(require_roles(*GESTION)),
):
    return use_cases["obtener_dashboard"].execute()
