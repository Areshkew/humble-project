from app.repositories.user_dao import UsuarioDAO
from app.repositories.userrole_dao import UsuarioRolDAO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
# from app.utils.db_utils import db_operation
import os, logging

from app.utils.db_utils import hash_password


class UserService:
    def __init__(self):
        self.logger = logging.getLogger("uvicorn")

    async def create_root_user(self, db: AsyncSession):
        """
            Crea un usuario Root en la base de datos si no existe.
        """
        # Preparar los datos de los roles:
        roles = [
            UsuarioRolDAO(nombre="root"),
            UsuarioRolDAO(nombre="admin"),
            UsuarioRolDAO(nombre="cliente")
        ]
        
        # Preparar los datos del usuario Root
        user_data = {
            "DNI": "R000000",
            "correo_electronico": os.getenv("ROOT_EMAIL"),
            "usuario": os.getenv("ROOT_USER"),
            "clave": hash_password( os.getenv("ROOT_PASSWORD") ),
            "rol": 1
        }
    
        # Verificar si el usuario Root ya existe
        stmt = select(UsuarioDAO).where(UsuarioDAO.DNI == user_data["DNI"])
        result = await db.execute(stmt)
        existing_user = result.scalars().first()

        if not existing_user:
            # Crear Roles
            db.add_all(roles)

            # Crear Usuario
            db_user = UsuarioDAO(**user_data)
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            self.logger.info("Se ha creado el usuario Root en la base de datos.")
        else:
            self.logger.info("El usuario Root ya existe en la base de datos.")

    async def get_user_dni_role(self, db: AsyncSession, email: str):
        """
            Obtener el usuario a través de su email.
        """
        stmt = select(UsuarioDAO.DNI, UsuarioRolDAO.nombre, UsuarioDAO.clave).join(UsuarioRolDAO, UsuarioDAO.rol == UsuarioRolDAO.id).where(UsuarioDAO.correo_electronico == email)
        result = await db.execute(stmt)
        user = result.fetchone()
        
        return {"DNI": user[0], "rol": user[1], "clave": user[2]} if user else None

    async def account_exists(self, db: AsyncSession, username: str, email: str, dni: str) -> bool:
        """
            Verifica si existe una cuenta con el mismo nombre de usuario, correo electrónico o DNI.
        """
        stmt = select(UsuarioDAO).where(
            (UsuarioDAO.usuario == username) | 
            (UsuarioDAO.correo_electronico == email) | 
            (UsuarioDAO.DNI == dni)
        )
        result = await db.execute(stmt)
        account = result.scalars().first()
        return account is not None
    
    async def create_account(self, db: AsyncSession, account_data: dict):
        """
            Crea una nueva cuenta de usuario en la base de datos.
        """
        new_account = UsuarioDAO(
            DNI=account_data["DNI"],
            nombre=account_data["nombre"],
            apellido=account_data["apellido"],
            fecha_nacimiento=account_data["fecha_nacimiento"],
            lugar_nacimiento=account_data["lugar_nacimiento"],
            direccion_envio=account_data["direccion_envio"],
            genero=account_data["genero"],
            correo_electronico=account_data["correo_electronico"],
            usuario=account_data["usuario"],
            clave=hash_password( account_data["clave"] ), 
            suscrito_noticias=account_data.get("suscrito_noticias", False), #TODO - Revisar cuando se le preguntará al usuario la suscripción a noticias.
            saldo=account_data.get("saldo", 0.0),
            rol=3 # Cliente
        )

        try:
            db.add(new_account)
            await db.commit()
            await db.refresh(new_account)
            return True
        except IntegrityError:
            await db.rollback()
            return None