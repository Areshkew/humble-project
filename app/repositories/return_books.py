from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base

class LibrosDevolucionDAO(Base):
    __tablename__ = 'libros_devolucion'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    codigo_devolucion = Column(Integer, ForeignKey('codigos_devolucion.id'), nullable=False) 
    id_libro = Column(String(16), ForeignKey('libros.ISSN'), nullable=False)  

    codigo_devolucion_ref = relationship("CodigoDevolucionDAO", back_populates="libros_devolucion")
    libro_ref = relationship("LibroDAO", back_populates="libros_devolucion")