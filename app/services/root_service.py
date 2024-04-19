from app.repositories.user_dao import UsuarioDAO
from app.utils.class_utils import Injectable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

class RootService(Injectable):
    async def get_admins(self, db: AsyncSession):
        """
            Devuelve todos los administradores disponibles.
        """
        stmt = select(UsuarioDAO.nombre, UsuarioDAO.apellido, 
                      UsuarioDAO.correo_electronico, UsuarioDAO.DNI, 
                      UsuarioDAO.pais).where(UsuarioDAO.rol == 2) # ADMIN ROLE id 2

        result = await db.execute(stmt)
        admins = result.all()

        if admins:
            admins_list = [
                {'nombre': admin[0], 'apellido': admin[1], 'correo_electronico': admin[2], 'DNI': admin[3], 'pais': admin[4]}
                for admin in admins
            ]
            return admins_list
        
        return None
    
    async def delete_admins(self, db: AsyncSession, dni_list: list):
        """
            Borrar administradores basado en una lista de DNI. 
        """
        stmt = delete(UsuarioDAO).where(UsuarioDAO.DNI.in_(dni_list), UsuarioDAO.rol == 2)
        result = await db.execute(stmt)
        
        await db.commit()
        return result.rowcount 
