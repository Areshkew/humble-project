from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class CodigoSeguridadDAO(Base):
    __tablename__ = 'codigos_seguridad'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    codigo = Column(String(8), unique=True , nullable=False)
    correo_electronico = Column(String(64), ForeignKey('usuarios.correo_electronico'), nullable=False, unique=True, index=True)
    fecha = Column(DateTime, nullable=False)

    correo_ref = relationship("UsuarioDAO", back_populates="codigos_ref")
