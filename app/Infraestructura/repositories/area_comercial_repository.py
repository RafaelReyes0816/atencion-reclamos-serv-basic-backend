from typing import List, Optional
from app.Domain.Repositories.area_comercial_repository import AreaComercialRepositoryABC
from app.Domain.Entities.area_comercial import AreaComercial
from app.Infraestructura.database.models.area_comercial import AreaComercialORM


class AreaComercialRepository(AreaComercialRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: AreaComercialORM) -> AreaComercial:
        return AreaComercial(
            id_area=orm.id_area,
            nombre=orm.nombre,
            tipo=orm.tipo,
            contacto=orm.contacto,
        )

    def get_all(self) -> List[AreaComercial]:
        query = self.db.query(AreaComercialORM)
        return [self._to_entity(e) for e in query.all()]

    def get_by_id(self, id: int) -> Optional[AreaComercial]:
        orm = self.db.query(AreaComercialORM).filter(AreaComercialORM.id_area == id).first()
        return self._to_entity(orm) if orm else None

    def create(self, data: dict) -> AreaComercial:
        orm = AreaComercialORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: AreaComercial) -> AreaComercial:
        orm = self.db.query(AreaComercialORM).filter(AreaComercialORM.id_area == entity.id_area).first()
        if orm:
            orm.nombre = entity.nombre
            orm.tipo = entity.tipo
            orm.contacto = entity.contacto
            self.db.commit()
            self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, id: int) -> None:
        orm = self.db.query(AreaComercialORM).filter(AreaComercialORM.id_area == id).first()
        if orm:
            self.db.delete(orm)
            self.db.commit()
