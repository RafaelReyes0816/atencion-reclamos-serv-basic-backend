from datetime import date

from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Repositories.medidor_repository import MedidorRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Domain.Entities.catalogos import EstadoReclamo
from app.Domain.Exceptions import NoEncontradoError
from app.Application.usecase.reclamo.validar_medidor import ValidarMedidorReclamoUseCase


class CrearReclamoUseCase:
    def __init__(
        self,
        reclamo_repo: ReclamoRepositoryABC,
        usuario_repo: UsuarioRepositoryABC,
        medidor_repo: MedidorRepositoryABC = None,
    ):
        self.reclamo_repo = reclamo_repo
        self.usuario_repo = usuario_repo
        self.medidor_repo = medidor_repo

    def execute(self, data: dict) -> Reclamo:
        data = dict(data)
        if not self.usuario_repo.get_by_id(data["id_usuario"]):
            raise NoEncontradoError("Usuario no encontrado")

        # El cliente no escribe el numero: elige el suyo. Y el medidor elegido tiene
        # que ser del servicio que se esta reclamando (el de agua para una fuga, el
        # de luz para un corte), porque de lo contrario la cuadrilla ira al lugar
        # equivocado.
        data["id_medidor"] = ValidarMedidorReclamoUseCase(self.medidor_repo).execute(
            id_usuario=data["id_usuario"],
            servicio=data.get("servicio"),
            id_medidor=data.pop("id_medidor", None),
        )

        data["fecha_recepcion"] = date.today()
        data["estado"] = EstadoReclamo.registrado.value
        return self.reclamo_repo.create(data)
