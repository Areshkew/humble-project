from sqlalchemy import Column, Integer, String, Date, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class MetodoPagoDAO(Base):
    __tablename__ = 'metodos_pago'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI'), nullable=False)
    tipo = Column(Integer, ForeignKey('tipo_metodos_pago.id'), nullable=False)
    num_tarjeta = Column(String(16), nullable=False)
    fec_vencimiento = Column(Date, nullable=False)
    cvv = Column(String(3), nullable=False)

    usuario_ref = relationship("UsuarioDAO", back_populates="metodos_pago")
    tipo_metodo_pago_ref = relationship("TipoMetodoPagoDAO", back_populates="metodos_pago")
