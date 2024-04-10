from sqlalchemy import Column, Integer, String, Date, Boolean, Float, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BYTEA
from db.base_class import Base

class LibroDAO(Base):
    __tablename__ = 'libros'
    ISSN = Column(String(16), primary_key=True, unique=True, nullable=False)
    titulo = Column(String(256), nullable=False)
    autor = Column(String(128), nullable=False)
    num_paginas = Column(Integer, nullable=False)
    idioma = Column(String(32), nullable=False)
    fecha_publicacion = Column(Date, nullable=False)
    estado = Column(Boolean, nullable=False)  # 0: Nuevo, 1: Usado
    portada = Column(String(256))
    precio = Column(Float, nullable=False)
    editorial = Column(Integer, ForeignKey('editoriales.id'), nullable=False)

    editorial_ref = relationship("EditorialDAO", back_populates="libros")
