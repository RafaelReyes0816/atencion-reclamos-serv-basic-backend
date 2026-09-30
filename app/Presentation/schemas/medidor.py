from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

from app.Domain.Entities.catalogos import Servicio

NUMERO = Field(
    min_length=4,
    max_length=30,
    pattern=r"^[A-Za-z0-9\-]+$",
    description="Numero del medidor, 4 a 30 caracteres alfanumericos y guiones",
)


class MedidorCreate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id_usuario: int = Field(gt=0)
    servicio: Servicio
    numero: str = NUMERO
    direccion: Optional[str] = Field(default=None, max_length=200)
    activo: bool = True


class MedidorUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    numero: Optional[str] = NUMERO
    direccion: Optional[str] = Field(default=None, max_length=200)
    activo: Optional[bool] = None


class MedidorResponse(BaseModel):
    id_medidor: int
    id_usuario: int
    servicio: str
    numero: str
    direccion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True


class MedidorCiudadanoResponse(BaseModel):
    """Ciudadano con sus medidores. Solo para los roles internos al registrar un reclamo.

    `direccion` es la del titular de la cuenta: el formulario de nuevo reclamo la
    prellena al elegir al ciudadano, asi que tiene que viajar en la misma respuesta
    y no en una consulta aparte por cada seleccion.
    """

    id_usuario: int
    documento: str
    nombre: str
    direccion: str = ""
    medidores: List[MedidorResponse]
