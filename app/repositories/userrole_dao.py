from sqlalchemy import Column, Integer, String, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class UsuarioRolDAO(Base):
    __tablename__ = 'usuarios_rol'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    nombre = Column(String(32), nullable=False)

    usuarios = relationship("UsuarioDAO", back_populates="rol_ref")