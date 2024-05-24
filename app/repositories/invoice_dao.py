from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship
 
class FacturaDAO(Base):
    __tablename__ = 'facturas'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    id_usuario = Column(String(10), ForeignKey('usuarios.DNI'), nullable=False)
    fecha = Column(Date, nullable=False)
    total = Column(Float, nullable=False)

    usuario_ref = relationship("UsuarioDAO", back_populates="facturas")
    pedidos = relationship("PedidoDAO", back_populates="factura_ref")