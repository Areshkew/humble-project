from sqlalchemy import Column, Integer, String
from db.base_class import Base
from sqlalchemy.orm import relationship

class TipoMetodoPagoDAO(Base):
    __tablename__ = 'tipo_metodos_pago'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    nombre_tipo = Column(String(32))

    metodos_pago = relationship("MetodoPagoDAO", back_populates="tipo_metodo_pago_ref")