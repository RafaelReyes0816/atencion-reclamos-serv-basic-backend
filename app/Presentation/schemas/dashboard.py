from pydantic import BaseModel, ConfigDict
from typing import List


class AlertaPlazo(BaseModel):
    id_reclamo: int
    estado: str
    fecha_tope: str
    dias_restantes: int


class AlertaCritico(BaseModel):
    id_reclamo: int
    servicio: str
    categoria: str
    urgencia: str
    estado: str


class MetricaServicio(BaseModel):
    servicio: str
    total: int


class DashboardResponse(BaseModel):
    total_reclamos: int
    total_usuarios: int
    por_estado: dict
    por_servicio: List[MetricaServicio]
    por_categoria: dict
    por_urgencia: dict
    en_atencion: int
    resueltos: int
    cerrados: int
    pendientes: int
    criticos: int
    vencidos: int
    proximos_vencer: int
    cumplidos_en_plazo: int
    cerrados_en_plazo: int
    porcentaje_cumplimiento: float
    alertas_vencidos: List[AlertaPlazo]
    alertas_vencimiento_proximo: List[AlertaPlazo]
    alertas_criticas: List[AlertaCritico]


class MensajeResponse(BaseModel):
    message: str
    status: str = "success"

    model_config = ConfigDict(from_attributes=True)
