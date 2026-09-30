from app.Domain.Repositories.medidor_repository import MedidorRepositoryABC
from app.Domain.Exceptions import NoEncontradoError, SinPermisosError, ValidacionError


class ValidarMedidorReclamoUseCase:
    """Regla de negocio: un reclamo siempre apunta al medidor correcto del cliente.

    Vive aparte porque la tienen que cumplir los tres caminos que tocan el medidor
    de un reclamo: crearlo, editarlo y reclasificarlo (que cambia el servicio y
    dejaria el medidor viejo apuntando al suministro equivocado).
    """

    def __init__(self, medidor_repo: MedidorRepositoryABC = None):
        self.medidor_repo = medidor_repo

    def execute(
        self,
        id_usuario: int,
        servicio: str,
        id_medidor: int,
        obligatorio: bool = True,
    ):
        """Devuelve el id del medidor ya verificado, o None si no aplica.

        `obligatorio=False` se usa al editar: si el cliente no manda medidor se
        conserva el que ya tenia el reclamo.
        """
        if self.medidor_repo is None:
            # Sin repositorio de medidores no hay nada que comprobar.
            return id_medidor

        if id_medidor is None:
            if obligatorio:
                raise ValidacionError("Debe seleccionar el medidor del suministro")
            return None

        medidor = self.medidor_repo.get_by_id(id_medidor)
        if medidor is None:
            raise NoEncontradoError("Medidor no encontrado")
        if medidor.id_usuario != id_usuario:
            raise SinPermisosError("El medidor seleccionado no pertenece a ese cliente")
        if medidor.servicio != servicio:
            raise ValidacionError(
                "El medidor seleccionado no corresponde al servicio del reclamo"
            )
        return medidor.id_medidor
