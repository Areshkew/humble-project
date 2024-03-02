from sqlalchemy import Column, Integer, String, Date, Boolean, Float, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class UsuarioDAO(Base):
    __tablename__ = 'usuarios'
    DNI = Column(String(10), primary_key=True, unique=True, nullable=False)
    nombre = Column(String(32))
    apellido = Column(String(32))
    fecha_nacimiento = Column(Date)
    lugar_nacimiento = Column(String(32))
    direccion_envio = Column(String(64))
    genero = Column(String(16))
    correo_electronico = Column(String(64), nullable=False)
    usuario = Column(String(32), nullable=False)
    clave = Column(String(128), nullable=False)
    suscrito_noticias = Column(Boolean)
    saldo = Column(Float)
    rol = Column(Integer, ForeignKey('usuarios_rol.id'))

    rol_ref = relationship("UsuarioRolDAO", back_populates="usuarios")