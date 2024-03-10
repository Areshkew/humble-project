from sqlalchemy import Column, Integer, String
from db.base_class import Base
from sqlalchemy.orm import relationship

class GeneroDAO(Base):
    __tablename__ = 'generos'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    genero = Column(String(64), nullable=False)

    libros_genero = relationship("LibroGeneroDAO", back_populates="genero_ref")
    preferencias_genero = relationship("PreferenciasDAO", back_populates="genero_ref")