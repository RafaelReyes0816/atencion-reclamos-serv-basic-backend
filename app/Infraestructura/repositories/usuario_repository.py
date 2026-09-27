from typing import List, Optional
from sqlalchemy.orm import joinedload
from app.Domain.Repositories.usuario_repository import UsuarioRepositoryABC
from app.Domain.Entities.usuario import Usuario
from app.Domain.Entities.catalogos import Rol
from app.Infraestructura.database.models.usuario import UsuarioORM
from app.Infraestructura.security import get_password_hash, verify_password


class UsuarioRepository(UsuarioRepositoryABC):
    def __init__(self, db):
        self.db = db

    def _to_entity(self, orm: UsuarioORM) -> Usuario:
        return Usuario(
            id_usuario=orm.id_usuario,
            nombre=orm.nombre,
            documento=orm.documento,
            telefono=orm.telefono,
            contraseña="",
            email=orm.email,
            direccion=orm.direccion,
            rol=orm.rol or Rol.ciudadano.value,
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

    def get_orm_by_documento(self, documento: str) -> Optional[UsuarioORM]:
        return self.db.query(UsuarioORM).filter(UsuarioORM.documento == documento).first()

    def create(self, data: dict) -> Usuario:
        data = dict(data)
        if "contraseña" in data:
            data["contraseña_hash"] = get_password_hash(data.pop("contraseña"))
        data.setdefault("rol", Rol.ciudadano.value)
        orm = UsuarioORM(**data)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, entity: Usuario) -> Usuario:
        orm = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == entity.id_usuario).first()
        if orm is None:
            raise ValueError(f"Usuario {entity.id_usuario} no encontrado")
        orm.nombre = entity.nombre
        orm.telefono = entity.telefono
        orm.email = entity.email
        orm.direccion = entity.direccion
        orm.rol = entity.rol
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def actualizar_contrasena(self, id: int, nueva_contrasena: str) -> None:
        orm = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == id).first()
        if orm is None:
            raise ValueError(f"Usuario {id} no encontrado")
        orm.contraseña_hash = get_password_hash(nueva_contrasena)
        self.db.commit()

    def verificar_contrasena(self, id: int, contrasena: str) -> bool:
        orm = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == id).first()
        if orm is None:
            return False
        return verify_password(contrasena, orm.contraseña_hash)

    def delete(self, id: int) -> None:
        orm = self.db.query(UsuarioORM).filter(UsuarioORM.id_usuario == id).first()
        if orm is None:
            raise ValueError(f"Usuario {id} no encontrado")
        if orm.reclamos:
            raise ValueError("No se puede eliminar un usuario con reclamos asociados")
        self.db.delete(orm)
        self.db.commit()
