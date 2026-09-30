from typing import List, Optional

from sqlalchemy.orm import joinedload

from app.Domain.Repositories.medidor_repository import MedidorRepositoryABC
from app.Domain.Entities.medidor import Medidor
from app.Infraestructura.database.models.medidor import MedidorORM
from app.Infraestructura.database.models.reclamo import ReclamoORM


class MedidorRepository(MedidorRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: MedidorORM) -> Medidor:
        return Medidor(
            id_medidor=orm.id_medidor,
            id_usuario=orm.id_usuario,
            servicio=orm.servicio,
            numero=orm.numero,
            direccion=orm.direccion,
            activo=orm.activo,
            usuario=orm.usuario,
        )

    def _base_query(self):
        return self.db.query(MedidorORM).options(joinedload(MedidorORM.usuario))

    def get_all(self) -> List[Medidor]:
        return [self._to_entity(e) for e in self._base_query().all()]

    def get_by_id(self, id: int) -> Optional[Medidor]:
        orm = self._base_query().filter(MedidorORM.id_medidor == id).first()
        return self._to_entity(orm) if orm else None

    def get_by_usuario(self, id_usuario: int) -> List[Medidor]:
        query = self._base_query().filter(MedidorORM.id_usuario == id_usuario).order_by(
            MedidorORM.servicio
        )
        return [self._to_entity(e) for e in query.all()]

    def get_por_servicio(self, id_usuario: int, servicio: str) -> Optional[Medidor]:
        orm = (
            self._base_query()
            .filter(MedidorORM.id_usuario == id_usuario, MedidorORM.servicio == servicio)
            .first()
        )
        return self._to_entity(orm) if orm else None

    def get_by_numero(self, numero: str) -> Optional[Medidor]:
        orm = self._base_query().filter(MedidorORM.numero == numero).first()
        return self._to_entity(orm) if orm else None

    def create(self, data: dict) -> Medidor:
        orm = MedidorORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: Medidor) -> Medidor:
        orm = self.db.query(MedidorORM).filter(MedidorORM.id_medidor == entity.id_medidor).first()
        if orm is None:
            raise ValueError(f"Medidor {entity.id_medidor} no encontrado")
        orm.servicio = entity.servicio
        orm.numero = entity.numero
        orm.direccion = entity.direccion
        orm.activo = entity.activo
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, id: int) -> None:
        orm = self.db.query(MedidorORM).filter(MedidorORM.id_medidor == id).first()
        if orm is None:
            raise ValueError(f"Medidor {id} no encontrado")
        # Los reclamos historicos no se borran: se quedan sin medidor asociado.
        self.db.query(ReclamoORM).filter(ReclamoORM.id_medidor == id).update(
            {ReclamoORM.id_medidor: None}, synchronize_session=False
        )
        self.db.delete(orm)
        self.db.commit()
