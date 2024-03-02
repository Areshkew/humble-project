from sqlalchemy import select
from app.repositories.user_dao import UsuarioDAO
# from app.utils.db_utils import db_operation
from sqlalchemy.ext.asyncio import AsyncSession
import os, logging

class UserService:
    async def create_root_user(self, db: AsyncSession):
        """
            Crea un usuario Root en la base de datos si no existe.
        """
        logger = logging.getLogger("uvicorn")

        # Preparar los datos del usuario Root
        user_data = {
            "DNI": "R000000",
            "correo_electronico": os.getenv("ROOT_EMAIL"),
            "usuario": os.getenv("ROOT_USER"),
            "clave": os.getenv("ROOT_PASSWORD")
        }
    
        # Verificar si el usuario Root ya existe
        stmt = select(UsuarioDAO).where(UsuarioDAO.DNI == user_data["DNI"])
        result = await db.execute(stmt)
        existing_user = result.scalars().first()

        if not existing_user:
            db_user = UsuarioDAO(**user_data)
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            logger.info("Se ha creado el usuario Root en la base de datos.")
        else:
            logger.info("El usuario Root ya existe en la base de datos.")