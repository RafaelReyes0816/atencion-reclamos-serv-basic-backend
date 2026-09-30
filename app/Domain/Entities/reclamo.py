from dataclasses import dataclass, field
from typing import Optional
from datetime import date


@dataclass
class Reclamo:
    id_reclamo: int
    id_usuario: int
    fecha_recepcion: date
    canal: str
    servicio: str
    categoria: str
    urgencia: str
    descripcion: str
    estado: str
    id_medidor: Optional[int] = None
    id_normativa: Optional[int] = None
    fecha_tope: Optional[date] = None
    fecha_cierre: Optional[date] = None
    resultado: Optional[str] = None
    # Derivado del medidor seleccionado, no se persiste en la tabla.
    numero_medidor: Optional[str] = None
    usuario: Optional[object] = field(default=None)
    normativa: Optional[object] = field(default=None)
    medidor: Optional[object] = field(default=None)
    orden_trabajo: Optional[object] = field(default=None)
    derivacion_comercial: Optional[object] = field(default=None)
