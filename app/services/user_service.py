from app.repositories.preferences_dao import PreferenciasDAO
from app.repositories.user_dao import UsuarioDAO
from app.repositories.userrole_dao import UsuarioRolDAO
from app.repositories.securitycodes_dao import CodigoSeguridadDAO
from app.utils.db_utils import hash_password
from app.utils.db_data import generos, roles, root_data
from app.utils.class_utils import Injectable
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete
import logging
import random


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


    async def get_user_data(self, db: AsyncSession, dni: str, user_fields: List[str]):
        """
        Obtiene los datos del usuario según el DNI y los campos especificados.
        """
        # Lista de campos a excluir 
        exclude_fields = ["clave", "preferencias"]

        selected_columns = [getattr(UsuarioDAO, field) for field in user_fields if field not in exclude_fields]

        # Realizar la consulta en la base de datos
        user_query = select(*selected_columns).filter(UsuarioDAO.DNI == dni)
        user_results = await db.execute(user_query)
        user_row = user_results.fetchone()

        # Crear un diccionario con los resultados
        user_data = dict(zip(user_fields, user_row))

        # Obtener las preferencias del usuario si se solicitan
        if "preferencias" in user_fields:
            preferences_query = select(PreferenciasDAO.id_genero).join(UsuarioDAO).filter(UsuarioDAO.DNI == dni)
            preferences_results = await db.execute(preferences_query)
            preferences = preferences_results.fetchall()
            user_data["preferencias"] = [pref[0] for pref in preferences]
            
        return user_data
    

    async def get_user_pass(self, db: AsyncSession, dni: str):
        """
            Obtener la pass del usuario
        """
        stmt = select(UsuarioDAO.clave).where(UsuarioDAO.DNI == dni)
        result = await db.execute(stmt)
        user = result.fetchone()
        
        return user[0]


    async def get_user_dni_role(self, db: AsyncSession, email: str): #Borrar
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
        stmt = select(
            UsuarioDAO.usuario,
            UsuarioDAO.correo_electronico,
            UsuarioDAO.DNI
        ).where(
            (UsuarioDAO.usuario == username) | 
            (UsuarioDAO.correo_electronico == email) | 
            (UsuarioDAO.DNI == dni)
        )
        result = await db.execute(stmt)
        account = result.first()
        
        fields_taken = {
            key: getattr(account, key, None) == value for key, value in {
                "usuario": username,
                "correo": email,
                "dni": dni
            }.items() if account and getattr(account, key, None) == value
        }

        return  {
            "exists": any(fields_taken.values()),
            "fields": fields_taken
        }
    

    async def create_account(self, db: AsyncSession, account_data: dict):
        """
            Crea una nueva cuenta de usuario en la base de datos.
        """
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
            clave= hash_password(account_data["clave"] ), 
            suscrito_noticias=account_data.get("suscrito_noticias", False),
            saldo=0.0,
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
        

    async def update_account(self, db: AsyncSession, account_data: dict, dni: str = ""):
        """
            Actualiza una cuenta de usuario en la base de datos.
        """
        
        result = await db.execute(select(UsuarioDAO).filter(UsuarioDAO.DNI == dni))
        user = result.scalar()

        if "fecha_nacimiento" in account_data:
            account_data["fecha_nacimiento"] = datetime.strptime(account_data["fecha_nacimiento"], "%Y-%m-%dT%H:%M:%S.%fZ").date()

        if "clave" in account_data:
            account_data["clave"] = hash_password(account_data["clave"])
        
        if "preferencias" in account_data:
            await db.execute(delete(PreferenciasDAO).where(PreferenciasDAO.id_usuario == dni))
            for preference in account_data["preferencias"]:
                new_preference = PreferenciasDAO(id_usuario=user.DNI, id_genero=preference["id"])
                db.add(new_preference) 
          
        try:    
            for key, value in account_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await db.commit()
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
        recovery_code = ''.join(random.choice(characters) for i in range(8))
        
        return recovery_code
    

    async def store_code(self, db: AsyncSession, email: str, code: str):
        """
        Crea una nueva instancia o actualiza el código de seguridad para el correo electrónico dado.
        """

        # Verificar si ya existe un registro para el correo electrónico dado
        existing_code = await db.execute(select(CodigoSeguridadDAO).filter(CodigoSeguridadDAO.correo_electronico == email))
        existing_code = existing_code.scalars().first()

        if existing_code: #Si existe actualizar
            existing_code.codigo = code
            existing_code.fecha = datetime.now()
            await db.commit()
        else: #Si no existe crear uno nuevo
            new_code = CodigoSeguridadDAO(
                codigo=code,
                correo_electronico=email,
                fecha=datetime.now()
            )
            try:
                db.add(new_code)
                await db.commit()
                return True
            except IntegrityError:
                await db.rollback()
                return False
    

    async def verify_code(self, db: AsyncSession, email: str, code: str) -> bool:
        """
        Compara si el correo tiene el codigo introducido asignado a el

        """
        stmt = select(CodigoSeguridadDAO).where( #Busqueda de correo y codigo especificados
            (CodigoSeguridadDAO.correo_electronico == email) &
            (CodigoSeguridadDAO.codigo == code)
        )
        result = await db.execute(stmt)
        codigo_seguridad = result.scalars().first()
        
        if codigo_seguridad is None:
            return False

        current_datetime = datetime.now()
        time_difference = current_datetime - codigo_seguridad.fecha

        if time_difference.total_seconds() < 300:  # 5 minutos en segundos
            return True
        else:
            return False

    
    async def update_password(self, db: AsyncSession, gmail: str, password: str, passwordRepeated: str) -> bool:
        """
        Actualiza la contraseña de algun email de un usuario

        """
        if password != passwordRepeated:
            return False

        hashed_password = hash_password(password)

        # Buscar al usuario por su correo electrónico en la base de datos
        user = await db.execute(select(UsuarioDAO).filter(UsuarioDAO.correo_electronico == gmail))
        user = user.scalars().first()
        if not user:
            return False

        # Actualizar la contraseña del usuario en la base de datos
        user.clave = hashed_password
        await db.commit()
        return True