from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Medidor:
    """Suministro asignado a un cliente.

    Cada usuario tiene como maximo un medidor por servicio (agua y luz). El par
    (id_usuario, servicio) es unico, asi que el cliente nunca tiene que escribir
    el numero: lo elige de los medidores que ya tiene dados de alta.
    """

    id_medidor: int
    id_usuario: int
    servicio: str
    numero: str
    direccion: Optional[str] = None
    activo: bool = True
    usuario: Optional[object] = field(default=None)
