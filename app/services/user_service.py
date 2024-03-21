from app.repositories.preferences_dao import PreferenciasDAO
from app.repositories.user_dao import UsuarioDAO
from app.repositories.userrole_dao import UsuarioRolDAO
from app.repositories.securitycodes_dao import CodigoSeguridadDAO
from app.utils.db_utils import hash_password
from app.utils.db_data import generos, roles, root_data
from app.utils.class_utils import Injectable
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import logging
import random
import datetime

class UserService(Injectable):
    def __init__(self):
        self.logger = logging.getLogger("uvicorn")

    @staticmethod
    async def initialize_db(db: AsyncSession):
        """
            Inicializar datos primordiales para el funcionamiento del software.
        """    
        # Verificar si el usuario Root ya existe
        stmt = select(UsuarioDAO).where(UsuarioDAO.DNI == root_data["DNI"])
        result = await db.execute(stmt)
        existing_user = result.scalars().first()

        if not existing_user:
            # Crear Roles
            db.add_all(roles)
            
            # Crear Generos
            db.add_all(generos)

            # Crear Usuario
            db_user = UsuarioDAO(**root_data)
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

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
        preferences = []
        birthDate_conversion = datetime.strptime(account_data["fecha_nacimiento"], "%Y-%m-%dT%H:%M:%S.%fZ").date()

        new_account = UsuarioDAO(
            DNI=account_data["DNI"],
            nombre=account_data["nombre"],
            apellido=account_data["apellido"],
            fecha_nacimiento=birthDate_conversion,
            pais=account_data["pais"],
            estado=account_data["estado"],
            ciudad=account_data["ciudad"],
            direccion_envio=account_data["direccion_envio"],
            genero=account_data["genero"],
            correo_electronico=account_data["correo_electronico"],
            usuario=account_data["usuario"],
            clave=hash_password( account_data["clave"] ), 
            suscrito_noticias=account_data.get("suscrito_noticias", False), #TODO - Revisar cuando se le preguntará al usuario la suscripción a noticias.
            saldo=0.0,
            rol=3 # Cliente
        )
        
        # Preferencias del usuario
        for preference in account_data["preferencias"]:
            preferences.append( PreferenciasDAO(id_usuario=account_data["DNI"], id_genero=preference["id"]) )

        try:
            db.add(new_account)
            db.add_all(preferences)
            await db.commit()
            await db.refresh(new_account)
            return True
        except IntegrityError:
            await db.rollback()
            return None
        
    async def generate_recovery_code(self) -> str:
        """
        Genera un código de recuperación de contraseña aleatorio de 8 caracteres alfanuméricos.

        """
        # Caracteres alfanuméricos que se utilizarán para generar el código
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # Genera el código de recuperación aleatorio
        recovery_code = await ''.join(random.choice(characters) for i in range(8))
        
        return recovery_code
    
    async def store_code(self, db: AsyncSession, email: str, code: str):
        """
            Crea nueva instancia para darle a un correo su codigo
        """

        current_datetime = datetime.datetime.now() #Guardar fecha de cuando se agrega el codigo a la db

        new_code = CodigoSeguridadDAO(
            codigo=code,
            correo_electronico=email,
            fecha= current_datetime
        )
        try:
            db.add(new_code)
            await db.commit()
            await db.refresh(new_code)
            return True
        except IntegrityError:
            await db.rollback()
            return None