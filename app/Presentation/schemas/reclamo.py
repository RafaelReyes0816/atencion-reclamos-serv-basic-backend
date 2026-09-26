from pydantic import BaseModel
from typing import Optional
from datetime import date


class ReclamoCreate(BaseModel):
    id_usuario: int
    canal: str
    servicio: str
    categoria: str
    urgencia: str
    descripcion: str


class ReclamoUpdate(BaseModel):
    id_normativa: Optional[int] = None
    estado: Optional[str] = None
    fecha_tope: Optional[date] = None
    fecha_cierre: Optional[date] = None
    resultado: Optional[str] = None


class ReclamoClasificar(BaseModel):
    servicio: str
    categoria: str
    urgencia: str


class ReclamoAsignarPlazo(BaseModel):
    id_normativa: int
    fecha_tope: date


class ReclamoResolver(BaseModel):
    resultado: str
    detalle: Optional[str] = None


class ReclamoCerrar(BaseModel):
    resultado: str


class ReclamoContactoUpdate(BaseModel):
    telefono: str
    email: Optional[str] = None


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

    class Config:
        from_attributes = True


class ComprobanteResponse(BaseModel):
    id_reclamo: int
    fecha_recepcion: date
    canal: str
    servicio: str
    categoria: str
    descripcion: str
    fecha_tope: Optional[date] = None
