from datetime import date
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.reclamo import Reclamo


class CrearReclamoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, usuario_repo: UsuarioRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.usuario_repo = usuario_repo

    def execute(self, data: dict) -> Reclamo:
        data["fecha_recepcion"] = date.today()
        data["estado"] = "registrado"
        return self.reclamo_repo.create(data)
