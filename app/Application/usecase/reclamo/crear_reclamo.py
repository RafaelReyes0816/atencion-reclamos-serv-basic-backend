from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Domain.Entities.catalogos import EstadoReclamo
from app.Domain.Exceptions import NoEncontradoError


class CrearReclamoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, usuario_repo: UsuarioRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.usuario_repo = usuario_repo

    def execute(self, data: dict) -> Reclamo:
        data = dict(data)
        if not self.usuario_repo.get_by_id(data["id_usuario"]):
            raise NoEncontradoError("Usuario no encontrado")
        data["fecha_recepcion"] = date.today()
        data["estado"] = EstadoReclamo.registrado.value
        return self.reclamo_repo.create(data)
