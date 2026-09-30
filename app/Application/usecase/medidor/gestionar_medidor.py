from typing import List, Optional
import secrets
import string

from app.Domain.Entities.medidor import Medidor
from app.Domain.Entities.catalogos import Servicio
from app.Domain.Repositories.medidor_repository import MedidorRepositoryABC
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Exceptions import (
    NoEncontradoError, DuplicadoError, ValidacionError,
)

SERVICIOS = (Servicio.agua.value, Servicio.luz.value)

# Sin vocales ni caracteres que se confundan al leerlo en voz alta o dictarlo por
# radio (0/O, 1/I/L, 5/S, 8/B, 2/Z).
CONFUSOS = set("OILSBZ")
ALFABETO = "".join(c for c in string.ascii_uppercase + string.digits if c not in CONFUSOS)
LARGO_SUFIJO = 8
MAX_INTENTOS = 20


def _prefijo(servicio: str) -> str:
    return "AG" if servicio == Servicio.agua.value else "LUZ"


def generar_numero_medidor(servicio: str) -> str:
    """Codigo que el sistema asigna al cliente al darle de alta su medidor.

    El cliente no elige el numero: el sistema lo genera, asi que cada recibo y cada
    reclamo apuntan al mismo suministro sin depender de que se lea bien a mano.
    """
    sufijo = "".join(secrets.choice(ALFABETO) for _ in range(LARGO_SUFIJO))
    return f"{_prefijo(servicio)}-{sufijo}"


def numero_medidor_aleatorio(servicio: str, medidor_repo: MedidorRepositoryABC) -> str:
    """Como `generar_numero_medidor`, pero reintenta si el codigo ya existe."""
    for _ in range(MAX_INTENTOS):
        candidato = generar_numero_medidor(servicio)
        if medidor_repo.get_by_numero(candidato) is None:
            return candidato
    raise DuplicadoError("No se pudo generar un numero de medidor libre, intente de nuevo")


class ListarMedidoresUseCase:
    def __init__(self, repository: MedidorRepositoryABC):
        self.repository = repository

    def execute(self, id_usuario: int) -> List[Medidor]:
        return self.repository.get_by_usuario(id_usuario)


class ObtenerMedidorUseCase:
    def __init__(self, repository: MedidorRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> Medidor:
        medidor = self.repository.get_by_id(id)
        if medidor is None:
            raise NoEncontradoError("Medidor no encontrado")
        return medidor


class ListarMedidoresDeCiudadanosUseCase:
    """Para los roles internos: ciudadanos con sus medidores, para registrar a su nombre."""

    def __init__(self, medidor_repo: MedidorRepositoryABC, usuario_repo: UsuarioRepositoryABC):
        self.medidor_repo = medidor_repo
        self.usuario_repo = usuario_repo

    def execute(self) -> List[dict]:
        resultado = []
        for usuario in self.usuario_repo.get_all():
            if usuario.rol != "ciudadano":
                continue
            resultado.append({
                "id_usuario": usuario.id_usuario,
                "documento": usuario.documento,
                "nombre": usuario.nombre,
                "medidores": self.medidor_repo.get_by_usuario(usuario.id_usuario),
            })
        return resultado


class CrearMedidorUseCase:
    def __init__(self, repository: MedidorRepositoryABC, usuario_repo: UsuarioRepositoryABC = None):
        self.repository = repository
        self.usuario_repo = usuario_repo

    def execute(self, data: dict) -> Medidor:
        data = dict(data)
        servicio = data.get("servicio")
        if servicio not in SERVICIOS:
            raise ValidacionError("El servicio debe ser 'agua' o 'luz'")
        # Sin esta comprobacion la llave foranea reventaria como error de base de
        # datos en vez de un 404 entendible.
        if self.usuario_repo is not None and not self.usuario_repo.get_by_id(data["id_usuario"]):
            raise NoEncontradoError("Usuario no encontrado")
        if self.repository.get_por_servicio(data["id_usuario"], servicio):
            raise DuplicadoError("El cliente ya tiene un medidor de ese servicio")
        data.setdefault("activo", True)
        return self.repository.create(data)


class ActualizarMedidorUseCase:
    def __init__(self, repository: MedidorRepositoryABC):
        self.repository = repository

    def execute(self, id: int, cambios: dict) -> Medidor:
        medidor = self.repository.get_by_id(id)
        if medidor is None:
            raise NoEncontradoError("Medidor no encontrado")
        for campo, valor in cambios.items():
            if valor is not None and hasattr(medidor, campo):
                setattr(medidor, campo, valor)
        return self.repository.update(medidor)


class EliminarMedidorUseCase:
    def __init__(self, repository: MedidorRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        if self.repository.get_by_id(id) is None:
            raise NoEncontradoError("Medidor no encontrado")
        self.repository.delete(id)


class AsignarMedidoresPorDefectoUseCase:
    """Da de alta el medidor de agua y el de luz de un cliente recien creado.

    Se ejecuta siempre, y es idempotente: si el cliente ya tiene el medidor de un
    servicio (por ejemplo, porque ya existia en la base), no lo duplica.
    """

    def __init__(self, medidor_repo: MedidorRepositoryABC, usuario_repo: UsuarioRepositoryABC = None):
        self.medidor_repo = medidor_repo
        self.usuario_repo = usuario_repo

    def execute(self, id_usuario: int, numeros: Optional[dict] = None) -> List[Medidor]:
        """Crea los medidores que falten. `numeros` fija numeros a mano; si no,
        el sistema genera un codigo por cada uno.
        """
        numeros = numeros or {}
        creados = []
        for servicio in SERVICIOS:
            if self.medidor_repo.get_por_servicio(id_usuario, servicio):
                continue
            numero = numeros.get(servicio) or numero_medidor_aleatorio(servicio, self.medidor_repo)
            creados.append(
                self.medidor_repo.create({
                    "id_usuario": id_usuario,
                    "servicio": servicio,
                    "numero": numero,
                    "activo": True,
                })
            )
        return creados
