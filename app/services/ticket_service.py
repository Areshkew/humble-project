from app.utils.class_utils import Injectable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.repositories.ticket_dao import TicketDAO
from app.repositories.ticketmsg_dao import TicketMensajeDAO
from sqlalchemy.exc import IntegrityError
from datetime import date

class TicketService(Injectable):
    async def create_ticket(self, db: AsyncSession, ticket_data: dict):
        """
        Crear un nuevo ticket en la base de datos 
        """
        new_ticket = TicketDAO(**ticket_data)

        try:
            db.add(new_ticket)
            await db.commit()
            #await db.refresh(new_ticket)
            return True
        except IntegrityError:
            await db.rollback()
            return None


    async def ticket_exist(self, db: AsyncSession, ticket_id: int):
        """
        Ver si un ticket existe en la base de datos
        """
        stmt = select(TicketDAO).where(TicketDAO.id == ticket_id)
        result = await db.execute(stmt)
        return result.scalars().first() is not None


    async def respond_to_ticket(self, db: AsyncSession, ticket_data: dict):
        """
        Crear respuesta a un ticket y guardar en la base de datos
        """

        ticket_data['fecha'] = date.today()

        new_message = TicketMensajeDAO(**ticket_data)
        try:
            db.add(new_message)
            await db.commit()
            #await db.refresh(new_message)
            return True
        except IntegrityError:
            await db.rollback()
            return None


    async def get_ticket_response(self, db: AsyncSession, ticket_id: int):
        """
        Buscar respuestas que tenga un ticket
        """
        stmt = select(TicketMensajeDAO).where(TicketMensajeDAO.id_ticket == ticket_id)
        result = await db.execute(stmt)
        response = result.scalars().all()
        return response
        

    async def delete_ticket(self, db: AsyncSession, ticket_id: int):
        """
        Eliminar un ticket en la base de datos
        """
        stmt = delete(TicketDAO).where(TicketDAO.id == ticket_id)
        await db.execute(stmt)
        await db.commit()

    async def get_user_tickets(self, db: AsyncSession, userId):
        '''
        Obtiene los tickets de un cliente con sus respectivos mensajes
        '''

        if userId == "all":
            stmt = select(TicketDAO.id, TicketDAO.asunto)
        else:
            stmt = select(TicketDAO.id, TicketDAO.asunto).where(TicketDAO.id_usuario == userId)
        tickets = await db.execute(stmt)
        tickets = tickets.fetchall()

        if tickets:
            totalChats = []
            for ticket_id, ticket_asunto in tickets:
                mensaje_stmt = select(
                    TicketMensajeDAO.id_usuario, 
                    TicketMensajeDAO.mensaje, 
                    TicketMensajeDAO.fecha  # Eliminar el formateo de la fecha
                ).where(TicketMensajeDAO.id_ticket == ticket_id)

                mensajes = await db.execute(mensaje_stmt)
                mensajes = mensajes.fetchall()
                
                # Convertir la fecha a un formato serializable
                mensajes = [(id_usuario, mensaje, fecha.strftime('%Y-%m-%d')) for id_usuario, mensaje, fecha in mensajes]
                
                totalChats.append({
                    "ticket_id": ticket_id,
                    "ticket_asunto": ticket_asunto,
                    "mensajes": mensajes
                })

            return totalChats
        else:
            return None
