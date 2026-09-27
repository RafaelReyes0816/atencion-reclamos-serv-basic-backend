from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from app.Domain.Entities.catalogos import TipoAreaComercial


class BaseCatalogo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class AreaComercialCreate(BaseCatalogo):
    nombre: str = Field(min_length=2, max_length=120)
    tipo: TipoAreaComercial
    contacto: str = Field(min_length=6, max_length=30)


class AreaComercialUpdate(BaseCatalogo):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    tipo: Optional[TipoAreaComercial] = None
    contacto: Optional[str] = Field(default=None, min_length=6, max_length=30)


class AreaComercialResponse(BaseModel):
    id_area: int
    nombre: str
    tipo: str
    contacto: str

    model_config = ConfigDict(from_attributes=True)
