from app.utils.class_utils import Injectable
from app.repositories.shop_dao import TiendaDAO
from app.utils.db_utils import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from datetime import datetime

class ShopService(Injectable):


    async def get_shops(self, db: AsyncSession):
        """
            Devuelve todos las tiendas disponibles.
        """
        shops = await db.execute(select(TiendaDAO))
        return shops.scalars().all()
    

    async def get_shop_by_id(self, shop_id: int, db: AsyncSession):
        """
            Devuelve una tienda segun una id
        """
        shop = await db.execute(select(TiendaDAO).filter(TiendaDAO.id == shop_id))
        return shop.scalar_one_or_none()


    async def create_shop(self, data: dict, db: AsyncSession):
        """
            Crear tienda con parametros dados
        """
        new_shop = TiendaDAO(
            ubicacion=data["ubicacion"],
            nombre=data["nombre"],
            num_contacto=data["num_contacto"],
            correo=data["correo"],
            hora_apertura = datetime.strptime(data["hora_apertura"], "%H:%M").time(),
            hora_cierre = datetime.strptime(data["hora_cierre"], "%H:%M").time()
        )
    
        db.add(new_shop)
        await db.commit()


    async def delete_shops(self, shop_ids: list, db: AsyncSession,):
        """
            Borrar tiendas basado en una lista de IDs
        """

        stmt = delete(TiendaDAO).where(TiendaDAO.id.in_(shop_ids))
        await db.execute(stmt)

        await db.commit()

    
    async def update_shop(self, shop_data: dict, shop_id: int, db: AsyncSession):
        shop = await db.get(TiendaDAO, shop_id)

        try:
            for key, value in shop_data.items():
                if key in ["hora_apertura", "hora_cierre"]:
                    setattr(shop, key, datetime.strptime(value, "%H:%M").time())
                else:
                    setattr(shop, key, value)
            await db.commit()

        except IntegrityError:
            await db.rollback()
            return None