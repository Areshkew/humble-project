from sqlalchemy import Column, Integer, String, Date, Boolean, Float, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class PreferenciasDAO(Base):
    __tablename__ = 'preferencias'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI', onupdate='CASCADE'))
    id_genero = Column(Integer, ForeignKey('generos.id'))
    
    usuario_ref = relationship("UsuarioDAO", back_populates="preferencias_usuario")
    genero_ref = relationship("GeneroDAO", back_populates="preferencias_genero")