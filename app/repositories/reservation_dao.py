from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base

class ReservaDAO(Base):
    __tablename__ = 'reservas'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI'), nullable=False)
    id_libro = Column(String(16), ForeignKey('libros.ISSN'), nullable=False)
    id_tienda = Column(Integer, ForeignKey('tienda.id'), nullable=False) 
    fecha_fin = Column(Date, nullable=False)

    usuario_ref = relationship("UsuarioDAO", back_populates="reservas")
    libro_ref = relationship("LibroDAO", back_populates="reservas")
    tienda_ref = relationship("TiendaDAO", back_populates="reservas")