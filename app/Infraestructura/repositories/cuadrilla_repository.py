from typing import List, Optional
from app.Domain.Repositories.cuadrilla_repository import CuadrillaRepositoryABC
from app.Domain.Entities.cuadrilla import Cuadrilla
from app.Infraestructura.database.models.cuadrilla import CuadrillaORM


class CuadrillaRepository(CuadrillaRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: CuadrillaORM) -> Cuadrilla:
        return Cuadrilla(
            id_cuadrilla=orm.id_cuadrilla,
            nombre=orm.nombre,
            especialidad=orm.especialidad,
            capacidad=orm.capacidad,
            contacto=orm.contacto,
        )

    def get_all(self) -> List[Cuadrilla]:
        query = self.db.query(CuadrillaORM)
        return [self._to_entity(e) for e in query.all()]

    def get_by_id(self, id: int) -> Optional[Cuadrilla]:
        orm = self.db.query(CuadrillaORM).filter(CuadrillaORM.id_cuadrilla == id).first()
        return self._to_entity(orm) if orm else None

    def get_by_id_con_bloqueo(self, id: int) -> Optional[Cuadrilla]:
        orm = self.db.query(CuadrillaORM).filter(
            CuadrillaORM.id_cuadrilla == id
        ).with_for_update().first()
        return self._to_entity(orm) if orm else None

    def get_disponibles(self, especialidad: str) -> List[Cuadrilla]:
        query = self.db.query(CuadrillaORM).filter(CuadrillaORM.especialidad == especialidad)
        return [self._to_entity(e) for e in query.all()]

    def create(self, data: dict) -> Cuadrilla:
        orm = CuadrillaORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: Cuadrilla) -> Cuadrilla:
        orm = self.db.query(CuadrillaORM).filter(CuadrillaORM.id_cuadrilla == entity.id_cuadrilla).first()
        if orm is None:
            raise ValueError(f"Cuadrilla {entity.id_cuadrilla} no encontrada")
        orm.nombre = entity.nombre
        orm.especialidad = entity.especialidad
        orm.capacidad = entity.capacidad
        orm.contacto = entity.contacto
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, id: int) -> None:
        orm = self.db.query(CuadrillaORM).filter(CuadrillaORM.id_cuadrilla == id).first()
        if orm is None:
            raise ValueError(f"Cuadrilla {id} no encontrada")
        self.db.delete(orm)
        self.db.commit()
