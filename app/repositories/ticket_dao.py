from sqlalchemy import Column, Integer, String, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class TicketDAO(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI'), nullable=False)

    usuario_ref = relationship("UsuarioDAO", back_populates="tickets")