from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.Infraestructura.database import Base


class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    documento = Column(String, unique=True, nullable=False, index=True)
    telefono = Column(String, nullable=False)
    email = Column(String, nullable=True)
    direccion = Column(String, nullable=False)

    reclamos = relationship("ReclamoORM", back_populates="usuario")
