from sqlalchemy import Column, Integer, ForeignKey, Date
from db.base_class import Base
from sqlalchemy.orm import relationship

class FacturaLibroDAO(Base):
    __tablename__ = 'facturas_libro'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_factura = Column(Integer, ForeignKey('facturas.id'), nullable=False)
    id_libro = Column(Integer, ForeignKey('libros_tienda.id'), nullable=False)
    estado = Column(Integer, nullable=False)  # 0: En Preparación, 1: Enviado, 2: Entregado, 3: Esperando Recogida
    fecha_fin = Column(Date, nullable=True)

    factura_ref = relationship("FacturaDAO", back_populates="facturas_libro")
    libro_tienda_ref = relationship("LibroTiendaDAO", back_populates="facturas_libro")