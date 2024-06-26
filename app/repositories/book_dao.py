from sqlalchemy import Column, Integer, String, Date, Boolean, Float, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from db.base_class import Base

class LibroDAO(Base):
    __tablename__ = 'libros'
    ISSN = Column(String(16), primary_key=True, unique=True, nullable=False)
    titulo = Column(String(256), nullable=False)
    autor = Column(String(256), nullable=False)
    resenia = Column(String, nullable=True)
    num_paginas = Column(Integer, nullable=False)
    idioma = Column(String(32), nullable=False)
    fecha_publicacion = Column(Date, nullable=False)
    estado = Column(Boolean, nullable=False)  # 1: Nuevo, 0: Usado
    portada = Column(String(256))
    precio = Column(Float, nullable=False)
    descuento = Column(Float, nullable=True)
    editorial = Column(Integer, ForeignKey('editoriales.id'), nullable=False)

    editorial_ref = relationship("EditorialDAO", back_populates="libros")
    reservas = relationship("ReservaDAO", back_populates="libro_ref")
    libros_devolucion = relationship("LibrosDevolucionDAO", back_populates="libro_ref")