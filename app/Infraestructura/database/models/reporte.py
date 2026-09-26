from sqlalchemy import Column, Integer, String, DateTime
from app.Infraestructura.database import Base


class ReporteORM(Base):
    __tablename__ = "reportes"

    id_reporte = Column(Integer, primary_key=True, index=True)
    tipo_reporte = Column(String, nullable=False)
    periodo = Column(String, nullable=False)
    fecha_generacion = Column(DateTime, nullable=False)
    contenido = Column(String, nullable=False)
