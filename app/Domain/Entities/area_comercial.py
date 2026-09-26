from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AreaComercial:
    id_area: int
    nombre: str
    tipo: str
    contacto: str
