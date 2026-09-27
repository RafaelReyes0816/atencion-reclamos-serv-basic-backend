from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Exceptions import ValidacionError


class CambiarContrasenaUseCase:
    def __init__(self, repository: UsuarioRepositoryABC):
        self.repository = repository

    def execute(self, id: int, contrasena_actual: str, contrasena_nueva: str) -> None:
        if not self.repository.verificar_contrasena(id, contrasena_actual):
            raise ValidacionError("La contraseña actual es incorrecta")
        if contrasena_actual == contrasena_nueva:
            raise ValidacionError("La contraseña nueva debe ser diferente de la actual")
        self.repository.actualizar_contrasena(id, contrasena_nueva)
