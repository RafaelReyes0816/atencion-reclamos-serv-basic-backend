from typing import List
from app.Domain.Repositories.cuadrilla_repository import CuadrillaRepositoryABC
from app.Domain.Entities.cuadrilla import Cuadrilla
from app.Domain.Exceptions import NoEncontradoError


def _con_carga(cuadrillas: List[Cuadrilla], orden_repo) -> List[Cuadrilla]:
    """Adjunta a cada cuadrilla cuantas ordenes activas lleva y si tiene cupo.

    El conteo es uno solo para toda la lista, no uno por cuadrilla. Se calcula
    en la lectura y no se guarda, asi que siempre refleja el estado real.
    """
    if orden_repo is None:
        return cuadrillas
    carga = orden_repo.contar_activas_por_cuadrilla() or {}
    for cuadrilla in cuadrillas:
        cuadrilla.ordenes_activas = carga.get(cuadrilla.id_cuadrilla, 0)
        cuadrilla.disponible = cuadrilla.ordenes_activas < cuadrilla.capacidad
    return cuadrillas


class ListarCuadrillasUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC, orden_repo=None):
        self.repository = repository
        self.orden_repo = orden_repo

    def execute(self) -> List[Cuadrilla]:
        return _con_carga(self.repository.get_all(), self.orden_repo)

    def execute_disponibles(self, especialidad: str) -> List[Cuadrilla]:
        cuadrillas = self.repository.get_disponibles(especialidad)
        # Con carga a la vista, la que mas trabajo tiene se ofrece primero: es
        # la que mas conviene para no dejar cuadrillas ociosas al lado.
        return sorted(
            _con_carga(cuadrillas, self.orden_repo),
            key=lambda c: (not c.disponible, c.ordenes_activas or 0, c.nombre),
        )


class ObtenerCuadrillaUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC, orden_repo=None):
        self.repository = repository
        self.orden_repo = orden_repo

    def execute(self, id: int) -> Cuadrilla:
        cuadrilla = self.repository.get_by_id(id)
        if cuadrilla is None:
            raise NoEncontradoError("Cuadrilla no encontrada")
        return _con_carga([cuadrilla], self.orden_repo)[0]


class CrearCuadrillaUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC):
        self.repository = repository

    def execute(self, data: dict) -> Cuadrilla:
        return self.repository.create(dict(data))


class ActualizarCuadrillaUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC, orden_repo=None):
        self.repository = repository
        self.orden_repo = orden_repo

    def execute(self, id: int, cambios: dict) -> Cuadrilla:
        cuadrilla = self.repository.get_by_id(id)
        if cuadrilla is None:
            raise NoEncontradoError("Cuadrilla no encontrada")

        # Bajar la capacidad por debajo de la carga actual es permitido, pero
        # avisado: la cuadrilla queda por encima de su tope y no aceptara
        # asignaciones nuevas hasta que se resuelvan ordenes o se amplie.
        nueva_capacidad = cambios.get("capacidad")
        if self.orden_repo is not None and nueva_capacidad is not None:
            activas = self.orden_repo.contar_activas_por_cuadrilla().get(id, 0)
            if nueva_capacidad < activas:
                cuadrilla.ordenes_activas = activas
                cuadrilla.disponible = False

        for campo, valor in cambios.items():
            if valor is not None and hasattr(cuadrilla, campo):
                setattr(cuadrilla, campo, valor)
        # Se recarga la carga despues de aplicar los cambios: si la capacidad
        # subio, la cuadrilla vuelve a estar disponible con los valores nuevos.
        return _con_carga([self.repository.update(cuadrilla)], self.orden_repo)[0]


class EliminarCuadrillaUseCase:
    def __init__(self, repository: CuadrillaRepositoryABC):
        self.repository = repository

    def execute(self, id: int) -> None:
        try:
            self.repository.delete(id)
        except ValueError as e:
            raise NoEncontradoError(str(e))
