from typing import Optional
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Exceptions import NoEncontradoError


class ActualizarContactoUseCase:
    def __init__(self, reclamo_repo: ReclamoRepositoryABC, usuario_repo: UsuarioRepositoryABC):
        self.reclamo_repo = reclamo_repo
        self.usuario_repo = usuario_repo

    def execute(
        self,
        id_reclamo: int,
        telefono: str,
        email: Optional[str],
        nombre_cuenta: Optional[str] = None,
        direccion: Optional[str] = None,
    ) -> None:
        reclamo = self.reclamo_repo.get_by_id(id_reclamo)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        usuario = self.usuario_repo.get_by_id(reclamo.id_usuario)
        if usuario is None:
            raise NoEncontradoError("Usuario no encontrado")
        # Telefono y email son del ciudadano que recibe las notificaciones.
        usuario.telefono = telefono
        usuario.email = email
        self.usuario_repo.update(usuario)
        # La cuenta y su direccion son del reclamo: pueden ser de un tercero.
        if nombre_cuenta is not None:
            reclamo.nombre_cuenta = nombre_cuenta.strip()
        if direccion is not None:
            reclamo.direccion = direccion.strip()
        self.reclamo_repo.update(reclamo)
