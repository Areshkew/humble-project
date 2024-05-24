from sqlalchemy import Column, Integer, String, Time
from db.base_class import Base
from sqlalchemy.orm import relationship

class TiendaDAO(Base):
    __tablename__ = 'tienda'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ubicacion = Column(String(64), nullable=False)
    nombre = Column(String(64), nullable=False)
    num_contacto = Column(String(10), nullable=False)
    correo = Column(String(64), nullable=False)
    hora_apertura = Column(Time, nullable=False)
    hora_cierre = Column(Time, nullable=False)

    libros_tienda = relationship("LibroTiendaDAO", back_populates="tienda_ref")
    reservas = relationship("ReservaDAO", back_populates="tienda_ref")