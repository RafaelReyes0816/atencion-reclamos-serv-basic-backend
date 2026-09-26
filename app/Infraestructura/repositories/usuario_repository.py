from typing import List, Optional
from sqlalchemy.orm import joinedload
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.usuario import Usuario
from app.Infraestructura.database.models.usuario import UsuarioORM


class UsuarioRepository(UsuarioRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: UsuarioORM) -> Usuario:
        return Usuario(
            id_usuario=orm.id_usuario,
            nombre=orm.nombre,
            documento=orm.documento,
            telefono=orm.telefono,
            email=orm.email,
            direccion=orm.direccion,
        )

    def get_all(self) -> List[Usuario]:
        query = self.db.query(UsuarioORM)
        return [self._to_entity(e) for e in query.all()]

    def get_by_id(self, id: int) -> Optional[Usuario]:
        orm = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == id).first()
        return self._to_entity(orm) if orm else None

    def get_by_documento(self, documento: str) -> Optional[Usuario]:
        orm = self.db.query(UsuarioORM).filter(UsuarioORM.documento == documento).first()
        return self._to_entity(orm) if orm else None

    def create(self, data: dict) -> Usuario:
        orm = UsuarioORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: Usuario) -> Usuario:
        orm = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == entity.id_usuario).first()
        if orm:
            orm.nombre = entity.nombre
            orm.telefono = entity.telefono
            orm.email = entity.email
            orm.direccion = entity.direccion
            self.db.commit()
            self.db.refresh(orm)
        return self._to_entity(orm)
