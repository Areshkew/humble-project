from app.utils.class_utils import Injectable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.repositories.paymentmethod_dao import MetodoPagoDAO
from app.repositories.user_dao import UsuarioDAO
from sqlalchemy.exc import IntegrityError

class PaymentService(Injectable):
    async def create_card(self, db: AsyncSession, card_data: dict):
        """
        Crear una nueva tarjeta en la base de datos 
        """
        new_card = MetodoPagoDAO(**card_data)

        try:
            db.add(new_card)
            await db.commit()
            await db.refresh(new_card)
            return True
        except IntegrityError:
            await db.rollback()
            return None
        

    async def card_exists(self, db: AsyncSession, num_tarjeta: str):
        """
        Mirar si una tarjeta existe en la base de datos
        """
        stmt = select(MetodoPagoDAO).where(MetodoPagoDAO.num_tarjeta == num_tarjeta)
        result = await db.execute(stmt)
        return result.scalars().first() is not None


    async def delete_card(self, db: AsyncSession, card_num: int):
        """
        Eliminar una tarjeta de la base de datos
        """
        stmt = delete(MetodoPagoDAO).where(MetodoPagoDAO.num_tarjeta == card_num)
        await db.execute(stmt)
        await db.commit()


    async def get_card(self, db: AsyncSession, card_num: int):
        """
        Obtener la informacion de una tarjeta en la base de datos
        """
        stmt = select(MetodoPagoDAO).where(MetodoPagoDAO.num_tarjeta == card_num)
        result = await db.execute(stmt)
        card = result.scalars().first()
        return card
    
    async def get_cards(self, db: AsyncSession, user_id: int):
        """
        Obtener la informacion de todas las tarjetas de un usuario
        """
        stmt = select(MetodoPagoDAO).where(MetodoPagoDAO.id_usuario == user_id)
        result = await db.execute(stmt)
        card = result.scalars().all()
        return card


    async def get_wallet(self, db: AsyncSession, user_id: int):
        """
        Obtener el saldo de un usuario 
        """
        stmt = select(UsuarioDAO.saldo).where(UsuarioDAO.DNI == user_id)
        result = await db.execute(stmt)
        wallet = result.scalars().all()
        return wallet
