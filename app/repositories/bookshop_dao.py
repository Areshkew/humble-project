from sqlalchemy import Column, Integer, ForeignKey, String
from db.base_class import Base
from sqlalchemy.orm import relationship

class LibroTiendaDAO(Base):
    __tablename__ = 'libros_tienda'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    id_tienda = Column(Integer, ForeignKey('tienda.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    ISSN = Column(String(16), ForeignKey('libros.ISSN', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    cantidad = Column(Integer)

    tienda_ref = relationship("TiendaDAO", back_populates="libros_tienda")
    libro_ref = relationship("LibroDAO")