from sqlalchemy import Column, Integer, String, Date, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship

class TicketMensajeDAO(Base):
    __tablename__ = 'tickets_mensajes'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_ticket = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    mensaje = Column(String(1024), nullable=False)
    fecha = Column(Date, nullable=False)

    ticket_ref = relationship("TicketDAO", back_populates="tickets_mensajes")