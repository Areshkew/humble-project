from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from db.base_class import Base
from sqlalchemy.orm import relationship

class MetodoPagoDAO(Base):
    __tablename__ = 'metodos_pago'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    tipo = Column(Boolean, nullable=False) # 0: Debito, 1: Credito
    num_tarjeta = Column(String(16), nullable=False)
    fec_vencimiento = Column(Date, nullable=False)
    cvv = Column(String(3), nullable=False)


    usuario_ref = relationship("UsuarioDAO", back_populates="metodos_pago")
