from pydantic import BaseModel
from typing import Optional
from datetime import date


class NormativaCreate(BaseModel):
    servicio: str
    categoria: str
    urgencia: str
    plazo_maximo_dias: int
    vigencia_desde: date


class NormativaUpdate(BaseModel):
    servicio: Optional[str] = None
    categoria: Optional[str] = None
    urgencia: Optional[str] = None
    plazo_maximo_dias: Optional[int] = None
    vigencia_desde: Optional[date] = None


class NormativaResponse(BaseModel):
    id_normativa: int
    servicio: str
    categoria: str
    urgencia: str
    plazo_maximo_dias: int
    vigencia_desde: date

    class Config:
        from_attributes = True
