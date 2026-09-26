from sqlalchemy import Column, Integer, String
from app.Infraestructura.database import Base


class CuadrillaORM(Base):
    __tablename__ = "cuadrillas"

    id_cuadrilla = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    especialidad = Column(String, nullable=False)
    capacidad = Column(Integer, nullable=False, default=1)
    contacto = Column(String, nullable=False)
