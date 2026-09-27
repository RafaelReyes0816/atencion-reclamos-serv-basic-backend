from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date
from app.Domain.Entities.catalogos import TipoAreaComercial, EstadoDerivacion


class BaseCatalogo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class DerivacionCreate(BaseCatalogo):
    id_reclamo: int = Field(gt=0)
    fecha_derivacion: date
    area_comercial: TipoAreaComercial


class DerivacionUpdate(BaseCatalogo):
    area_comercial: Optional[TipoAreaComercial] = None
    fecha_derivacion: Optional[date] = None
    estado_derivacion: Optional[EstadoDerivacion] = None


class DerivacionResponse(BaseModel):
    id_derivacion: int
    id_reclamo: int
    fecha_derivacion: date
    area_comercial: str
    estado_derivacion: str

    model_config = ConfigDict(from_attributes=True)
