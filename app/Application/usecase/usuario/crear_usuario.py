from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.usuario import Usuario
from app.Domain.Entities.catalogos import Rol
from app.Domain.Exceptions import DuplicadoError


class CrearUsuarioUseCase:
    def __init__(self, repository: UsuarioRepositoryABC, asignar_medidores=None):
        self.repository = repository
        # Caso opcional para no romper los tests que construyen el caso de uso aislado.
        self.asignar_medidores = asignar_medidores

    def execute(self, data: dict, rol: str = Rol.ciudadano.value) -> Usuario:
        data = dict(data)
        if self.repository.get_by_documento(data["documento"]):
            raise DuplicadoError("Ya existe un usuario con ese documento")
        data["direccion"] = data.get("direccion") or ""
        data["rol"] = rol
        usuario = self.repository.create(data)
        if self.asignar_medidores is not None:
            # Todo cliente nace con su medidor de agua y el de luz dados de alta, con
            # un codigo que genera el sistema, para que al registrar un reclamo solo
            # tenga que seleccionar uno.
            self.asignar_medidores.execute(usuario.id_usuario)
        return usuario
