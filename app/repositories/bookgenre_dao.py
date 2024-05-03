from sqlalchemy import Column, Integer, ForeignKey, String
from db.base_class import Base
from sqlalchemy.orm import relationship

class LibroGeneroDAO(Base):
    __tablename__ = 'libros_genero'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_genero = Column(Integer, ForeignKey('generos.id', onupdate='CASCADE'), nullable=False)
    ISSN = Column(String(16), ForeignKey('libros.ISSN', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    genero_ref = relationship("GeneroDAO", back_populates="libros_genero")
    libro_ref = relationship("LibroDAO")