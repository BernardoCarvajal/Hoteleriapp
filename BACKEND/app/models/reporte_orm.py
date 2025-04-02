from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class ReporteORM(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    parametros = Column(JSON, nullable=True)
    
    # Aquí se podría almacenar el reporte generado en formato JSON o en otro formato
    # dependiendo de los requisitos específicos 