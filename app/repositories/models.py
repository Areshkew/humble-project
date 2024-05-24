from .book_dao import LibroDAO
from .bookgenre_dao import LibroGeneroDAO
from .bookshop_dao import LibroTiendaDAO
from .cupon_dao import CuponDAO
from .genre_dao import GeneroDAO
from .invoice_dao import FacturaDAO
from .invoicebook_dao import FacturaLibroDAO
from .paymentmethod_dao import MetodoPagoDAO
from .order_dao import PedidoDAO
from .publishing_dao import EditorialDAO
from .reservation_dao import ReservaDAO
from .shop_dao import TiendaDAO
from .ticket_dao import TicketDAO
from .ticketmsg_dao import TicketMensajeDAO
from .user_dao import UsuarioDAO
from .userrole_dao import UsuarioRolDAO
from .preferences_dao import PreferenciasDAO
from .securitycodes_dao import CodigoSeguridadDAO
from sqlalchemy.orm import relationship

# Creación de las relaciones entre las tablas
UsuarioDAO.cupones = relationship("CuponDAO", back_populates="usuario_ref")
UsuarioDAO.metodos_pago = relationship("MetodoPagoDAO", back_populates="usuario_ref")
UsuarioDAO.reservas = relationship("ReservaDAO", back_populates="usuario_ref")
UsuarioDAO.facturas = relationship("FacturaDAO", back_populates="usuario_ref")
UsuarioDAO.tickets = relationship("TicketDAO", back_populates="usuario_ref")
UsuarioDAO.ticketsmsg = relationship("TicketMensajeDAO", back_populates="usuario_ref")
LibroDAO.reservas = relationship("ReservaDAO", back_populates="libro_ref")
LibroTiendaDAO.facturas_libro = relationship("FacturaLibroDAO", back_populates="libro_tienda_ref")
FacturaDAO.facturas_libro = relationship("FacturaLibroDAO", back_populates="factura_ref")
TicketDAO.tickets_mensajes = relationship("TicketMensajeDAO", back_populates="ticket_ref")
TiendaDAO.pedidos = relationship("PedidoDAO", back_populates="tienda_ref")
TiendaDAO.reservas = relationship("ReservaDAO", back_populates="tienda_ref")