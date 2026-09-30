from typing import List
from app.Domain.Repositories.orden_trabajo_repository import OrdenTrabajoRepositoryABC
from app.Domain.Repositories.reclamo_repository import ReclamoRepositoryABC
from app.Domain.Repositories.avance_repository import AvanceRepositoryABC
from app.Domain.Entities.orden_trabajo import OrdenTrabajo
from app.Domain.Entities.catalogos import EstadoOrden
from app.Domain.Exceptions import NoEncontradoError, ConflictoError

# Invariante compartida: una atencion tecnica no se culmina sin avances.
SIN_AVANCES = "La orden de trabajo no tiene avances registrados; regístralos antes de resolver"


def _resolver_cuadrilla(orden_repo, cuadrilla_repo, id_cuadrilla, excluir_id_orden=None):
    """Bloquea la cuadrilla y devuelve su entidad si todavia tiene cupo.

    Bloquear antes de contar es lo que evita que dos asignaciones simultaneas
    pasen las dos el control sobre la ultima plaza disponible.

    `excluir_id_orden` descuenta la orden que se esta moviendo, para que
    reasignar una orden a su misma cuadrilla no se bloquee a si misma.
    """
    cuadrilla = cuadrilla_repo.get_by_id_con_bloqueo(id_cuadrilla)
    if cuadrilla is None:
        raise NoEncontradoError(f"Cuadrilla {id_cuadrilla} no encontrada")

    carga = orden_repo.contar_activas_por_cuadrilla(excluir_id_orden).get(id_cuadrilla, 0)
    if carga >= cuadrilla.capacidad:
        raise ConflictoError(
            f"La cuadrilla {cuadrilla.nombre} ya tiene {carga} de {cuadrilla.capacidad} "
            "órdenes activas; su capacidad está agotada. Amplíala o asigná otra cuadrilla."
        )
    return cuadrilla


class ListarOrdenesUseCase:
    def __init__(self, repository: OrdenTrabajoRepositoryABC):
        self.repository = repository

    def execute(self) -> List[OrdenTrabajo]:
        return self.repository.get_all()


class ObtenerOrdenUseCase:
    def __init__(self, repository: OrdenTrabajoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> OrdenTrabajo:
        orden = self.repository.get_by_id(id)
        if orden is None:
            raise NoEncontradoError("Orden no encontrada")
        return orden

    def execute_por_reclamo(self, id_reclamo: int) -> OrdenTrabajo:
        orden = self.repository.get_by_reclamo(id_reclamo)
        if orden is None:
            raise NoEncontradoError("No hay orden para este reclamo")
        return orden


class CrearOrdenUseCase:
    # `cuadrilla_repo` es obligatorio a proposito: sin el no hay forma de
    # validar la capacidad, y un default None la omitiria en silencio.
    def __init__(self, orden_repo: OrdenTrabajoRepositoryABC, reclamo_repo, cuadrilla_repo):
        self.orden_repo = orden_repo
        self.reclamo_repo = reclamo_repo
        self.cuadrilla_repo = cuadrilla_repo

    def execute(self, data: dict) -> OrdenTrabajo:
        reclamo = self.reclamo_repo.get_by_id(data["id_reclamo"])
        if not reclamo:
            raise NoEncontradoError("Reclamo no encontrado")
        if self.orden_repo.get_by_reclamo(data["id_reclamo"]):
            raise ConflictoError("El reclamo ya tiene una orden de trabajo")

        data = dict(data)
        id_cuadrilla = data.pop("id_cuadrilla", None)
        if id_cuadrilla is not None:
            cuadrilla = _resolver_cuadrilla(self.orden_repo, self.cuadrilla_repo, id_cuadrilla)
            # El nombre lo pone el servidor desde la fila de la cuadrilla: si
            # el cliente tambien lo mandara, id y nombre podrian contradecirse.
            data["cuadrilla"] = cuadrilla.nombre
            data["id_cuadrilla"] = cuadrilla.id_cuadrilla

        data["estado_orden"] = "asignada"
        orden = self.orden_repo.create(data)
        self.reclamo_repo.update_estado(reclamo.id_reclamo, "en_atencion_tecnica")
        return orden


class ActualizarOrdenUseCase:
    def __init__(
        self,
        repository: OrdenTrabajoRepositoryABC,
        reclamo_repo: ReclamoRepositoryABC,
        avance_repo: AvanceRepositoryABC,
        cuadrilla_repo,
    ):
        self.repository = repository
        self.reclamo_repo = reclamo_repo
        self.avance_repo = avance_repo
        self.cuadrilla_repo = cuadrilla_repo

    def execute(self, id: int, cambios: dict) -> OrdenTrabajo:
        orden = self.repository.get_by_id(id)
        if orden is None:
            raise NoEncontradoError("Orden no encontrada")

        # Cambiar de cuadrilla es asignarle trabajo a otra, asi que pasa por el
        # mismo control de capacidad. Se excluye esta orden del conteo: si se
        # queda en la misma, no debe bloquearse a si misma.
        cambios = dict(cambios)
        id_cuadrilla = cambios.get("id_cuadrilla")
        if id_cuadrilla is not None:
            cuadrilla = _resolver_cuadrilla(
                self.repository, self.cuadrilla_repo, id_cuadrilla, excluir_id_orden=id
            )
            cambios["cuadrilla"] = cuadrilla.nombre

        # Una orden no se resuelve sin al menos un avance que lo respalde. Se
        # valida antes de mutar para no dejar cambios a medias.
        if cambios.get("estado_orden") == EstadoOrden.resuelta.value and not (
            self.avance_repo.get_by_orden(id)
        ):
            raise ConflictoError(SIN_AVANCES)
        for campo, valor in cambios.items():
            if valor is not None and hasattr(orden, campo):
                setattr(orden, campo, valor)
        resultado = self.repository.update(orden)
        if (
            self.reclamo_repo
            and cambios.get("estado_orden") == EstadoOrden.resuelta.value
            and orden.id_reclamo
        ):
            self.reclamo_repo.update_estado(orden.id_reclamo, "resuelto")
        return resultado


class EliminarOrdenUseCase:
    def __init__(self, repository: OrdenTrabajoRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            raise NoEncontradoError(str(e))
