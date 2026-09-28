from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import date
from app.Domain.Entities.catalogos import (
    Canal, Servicio, Categoria, Urgencia, EstadoReclamo, Resultado
)


class BaseCatalogo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class ReclamoCreate(BaseCatalogo):
    id_usuario: int = Field(gt=0)
    canal: Canal
    servicio: Servicio
    categoria: Categoria
    urgencia: Urgencia
    descripcion: str = Field(min_length=5, max_length=1000)
    nombre_cuenta: str = Field(min_length=3, max_length=120)
    direccion: str = Field(min_length=5, max_length=255)


class ReclamoUpdate(BaseCatalogo):
    canal: Optional[Canal] = None
    servicio: Optional[Servicio] = None
    categoria: Optional[Categoria] = None
    urgencia: Optional[Urgencia] = None
    descripcion: Optional[str] = Field(default=None, min_length=5, max_length=1000)
    nombre_cuenta: Optional[str] = Field(default=None, min_length=3, max_length=120)
    direccion: Optional[str] = Field(default=None, min_length=5, max_length=255)
    id_normativa: Optional[int] = None
    estado: Optional[EstadoReclamo] = None
    fecha_tope: Optional[date] = None
    fecha_cierre: Optional[date] = None
    resultado: Optional[Resultado] = None


class ReclamoClasificar(BaseCatalogo):
    servicio: Servicio
    categoria: Categoria
    urgencia: Urgencia


class ReclamoAsignarPlazo(BaseCatalogo):
    id_normativa: int = Field(gt=0)
    fecha_tope: date


class ReclamoResolver(BaseCatalogo):
    resultado: Resultado
    detalle: Optional[str] = Field(default=None, max_length=1000)


class ReclamoCerrar(BaseCatalogo):
    resultado: Resultado


class ReclamoContactoUpdate(BaseCatalogo):
    telefono: str = Field(min_length=6, max_length=30)
    email: Optional[EmailStr] = None
    nombre_cuenta: Optional[str] = Field(default=None, min_length=3, max_length=120)
    direccion: Optional[str] = Field(default=None, min_length=5, max_length=255)


class ReclamoFiltros(BaseCatalogo):
    estado: Optional[EstadoReclamo] = None
    servicio: Optional[Servicio] = None
    categoria: Optional[Categoria] = None
    urgencia: Optional[Urgencia] = None
    canal: Optional[Canal] = None
    id_usuario: Optional[int] = Field(default=None, gt=0)


class ReclamoResponse(BaseModel):
    id_reclamo: int
    id_usuario: int
    fecha_recepcion: date
    canal: str
    servicio: str
    categoria: str
    urgencia: str
    descripcion: str
    estado: str
    id_normativa: Optional[int] = None
    fecha_tope: Optional[date] = None
    fecha_cierre: Optional[date] = None
    resultado: Optional[str] = None
    nombre_cuenta: Optional[str] = None
    direccion: Optional[str] = None

    class Config:
        from_attributes = True


class ComprobanteResponse(BaseModel):
    id_reclamo: int
    fecha_recepcion: date
    canal: str
    servicio: str
    categoria: str
    descripcion: str
    nombre_cuenta: Optional[str] = None
    direccion: Optional[str] = None
    fecha_tope: Optional[date] = None
