from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.medidor_repository import MedidorRepositoryABC
from app.Domain.Entities.reclamo import Reclamo
from app.Domain.Entities.catalogos import EstadoReclamo
from app.Domain.Exceptions import NoEncontradoError, ConflictoError
from app.Application.usecase.reclamo.validar_medidor import ValidarMedidorReclamoUseCase


class ActualizarReclamoUseCase:
    def __init__(
        self,
        repository: ReclamoRepositoryABC,
        medidor_repo: MedidorRepositoryABC = None,
    ):
        self.repository = repository
        self.medidor_repo = medidor_repo

    def execute(self, id: int, cambios: dict) -> Reclamo:
        reclamo = self.repository.get_by_id(id)
        if reclamo is None:
            raise NoEncontradoError("Reclamo no encontrado")
        if reclamo.estado == EstadoReclamo.cerrado.value:
            raise ConflictoError("No se puede modificar un reclamo cerrado")

        cambios = {campo: valor for campo, valor in cambios.items() if valor is not None}
        # El servicio y el medidor se validan juntos: cambiar uno sin el otro
        # dejaria el reclamo apuntando al suministro equivocado.
        if "id_medidor" in cambios or "servicio" in cambios:
            nuevo_medidor = cambios.get("id_medidor", reclamo.id_medidor)
            nuevo_servicio = cambios.get("servicio", reclamo.servicio)
            if nuevo_medidor is not None:
                cambios["id_medidor"] = ValidarMedidorReclamoUseCase(self.medidor_repo).execute(
                    id_usuario=reclamo.id_usuario,
                    servicio=nuevo_servicio,
                    id_medidor=nuevo_medidor,
                    obligatorio=False,
                )

        for campo, valor in cambios.items():
            if hasattr(reclamo, campo):
                setattr(reclamo, campo, valor)
        return self.repository.update(reclamo)


class EliminarReclamoUseCase:
    def __init__(self, repository: ReclamoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            raise NoEncontradoError(str(e))
