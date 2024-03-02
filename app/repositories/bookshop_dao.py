from sqlalchemy import Column, Integer, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class LibroTiendaDAO(Base):
    __tablename__ = 'libros_tienda'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_tienda = Column(Integer, ForeignKey('tienda.id'), nullable=False)
    ISSN = Column(Integer, ForeignKey('libros.ISSN'), nullable=False)

    tienda_ref = relationship("TiendaDAO", back_populates="libros_tienda")
    libro_ref = relationship("LibroDAO")