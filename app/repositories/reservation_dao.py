from sqlalchemy import Column, Integer, String, Date, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class ReservaDAO(Base):
    __tablename__ = 'reservas'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI'), nullable=False)
    id_libro = Column(Integer, ForeignKey('libros_tienda.id'), nullable=False)
    fecha_fin = Column(Date, nullable=False)

    usuario_ref = relationship("UsuarioDAO", back_populates="reservas")
    libro_tienda_ref = relationship("LibroTiendaDAO", back_populates="reservas")