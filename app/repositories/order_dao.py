from sqlalchemy import Column, Integer, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class PedidoDAO(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_tienda = Column(Integer, ForeignKey('tienda.id'), nullable=False)
    id_factura = Column(Integer, ForeignKey('facturas.id'), nullable=False)
    estado = Column(Integer, nullable=False)  # 0: En Preparación, 1: Enviado, 2: Entregado, 3: Esperando Recogida

    tienda_ref = relationship("TiendaDAO", back_populates="pedidos")
    factura_ref = relationship("FacturaDAO", back_populates="pedidos")