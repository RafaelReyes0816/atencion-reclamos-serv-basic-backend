from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from app.Domain.Entities.catalogos import Servicio, Categoria, Urgencia


class BaseCatalogo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class NormativaCreate(BaseCatalogo):
    servicio: Servicio
    categoria: Categoria
    urgencia: Urgencia
    plazo_maximo_dias: int = Field(gt=0, le=3650)
    vigencia_desde: date


class NormativaUpdate(BaseCatalogo):
    servicio: Optional[Servicio] = None
    categoria: Optional[Categoria] = None
    urgencia: Optional[Urgencia] = None
    plazo_maximo_dias: Optional[int] = Field(default=None, gt=0, le=3650)
    vigencia_desde: Optional[date] = None


class NormativaFiltros(BaseCatalogo):
    servicio: Optional[Servicio] = None
    categoria: Optional[Categoria] = None
    urgencia: Optional[Urgencia] = None


class NormativaResponse(BaseModel):
    id_normativa: int
    servicio: str
    categoria: str
    urgencia: str
    plazo_maximo_dias: int
    vigencia_desde: date

    model_config = ConfigDict(from_attributes=True)
