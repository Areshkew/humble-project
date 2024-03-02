from sqlalchemy import Column, String, Date, Float, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class CuponDAO(Base):
    __tablename__ = 'cupones'
    codigo_redencion = Column(String(8), primary_key=True, unique=True, nullable=False)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI'), nullable=False)
    fecha = Column(Date)
    porcentaje = Column(Float)

    usuario_ref = relationship("UsuarioDAO", back_populates="cupones")