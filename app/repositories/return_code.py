from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base

class CodigoDevolucionDAO(Base):
    __tablename__ = 'codigos_devolucion'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI'), nullable=False)
    fecha_fin = Column(Date, nullable=False)
    
    usuario_ref = relationship("UsuarioDAO", back_populates="codigos_devolucion")
    libros_devolucion = relationship("LibrosDevolucionDAO", back_populates="codigo_devolucion_ref")