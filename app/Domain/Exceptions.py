class DomainError(Exception):
    """Error de negocio base. La capa Presentation lo traduce a un codigo HTTP."""

    status_code = 400

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontradoError(DomainError):
    status_code = 404


class ConflictoError(DomainError):
    status_code = 409


class DuplicadoError(DomainError):
    """Un registro con el mismo identificador unico ya existe."""

    status_code = 400


class ValidacionError(DomainError):
    status_code = 422


class SinPermisosError(DomainError):
    status_code = 403
