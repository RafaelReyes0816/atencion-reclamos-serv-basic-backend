from sqlalchemy import Column, Integer, String
from app.Infraestructura.database import Base


class AreaComercialORM(Base):
    __tablename__ = "areas_comerciales"

    id_area = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    contacto = Column(String, nullable=False)
