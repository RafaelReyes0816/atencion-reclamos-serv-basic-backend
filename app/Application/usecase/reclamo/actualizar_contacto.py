from typing import Optional
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Exceptions import NoEncontradoError


class ActualizarContactoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, usuario_repo: UsuarioRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.usuario_repo = usuario_repo

    def execute(self, id_reclamo: int, telefono: str, email: Optional[str]) -> None:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        usuario = self.usuario_repo.get_by_id(reclamo.id_usuario)
        if usuario is None:
            raise NoEncontradoError("Usuario no encontrado")
        usuario.telefono = telefono
        usuario.email = email
        self.usuario_repo.update(usuario)
