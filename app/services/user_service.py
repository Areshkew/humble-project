from app.repositories.preferences_dao import PreferenciasDAO
from app.repositories.securitycodes_dao import CodigoSeguridadDAO
from app.repositories.user_dao import UsuarioDAO
from app.repositories.userrole_dao import UsuarioRolDAO
from app.repositories.invoice_dao import FacturaDAO
from app.repositories.invoicebook_dao import FacturaLibroDAO
from app.repositories.reservation_dao import ReservaDAO
from app.repositories.shop_dao import TiendaDAO
from app.repositories.bookshop_dao import LibroTiendaDAO
from app.repositories.book_dao import LibroDAO
from app.repositories.return_code import CodigoDevolucionDAO
from app.repositories.return_books import LibrosDevolucionDAO
from app.utils.class_utils import Injectable
from app.utils.db_data import generos, roles, root_data
from app.utils.db_utils import hash_password
from datetime import datetime, timedelta
from sqlalchemy import select, delete, func, update
from sqlalchemy.sql import join
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
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
                "correo_electronico": email,
                "dni": dni
            }.items() if account and getattr(account, key, None) == value
        }

        return  {
            "exists": any(fields_taken.values()),
            "fields": fields_taken
        }
    

    async def create_account(self, db: AsyncSession, account_data: dict, role: int = 3):
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
            rol=role # Cliente
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
        characters = '0123456789'
        
        # Genera el código de recuperación aleatorio
        recovery_code = ''.join(random.choice(characters) for i in range(6))
        
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

    
    async def update_password(self, db: AsyncSession, gmail: str, password: str) -> bool:
        """
        Actualiza la contraseña de algun email de un usuario

        """
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
    
    async def saldo_user(self, id: str, db: AsyncSession) -> str:
        """
        Obtiene el saldo del user por el ID
        """
        saldo = await db.execute(
            select(UsuarioDAO.saldo)
                .where(UsuarioDAO.DNI == id)
            )
        
        if saldo:
            return saldo.first()[0]
        else:
            return None
        
    async def get_user_email(self, id: str, db: AsyncSession) -> str:
        """
        Obtiene el email del user por el ID
        """
        correo_electronico = await db.execute(
            select(UsuarioDAO.correo_electronico)
                .where(UsuarioDAO.DNI == id)
            )
        
        if correo_electronico:
            return correo_electronico.first()[0]
        else:
            return None  
        
    async def facturas_user(self, id: str, db: AsyncSession) -> str:
        """
        Obtiene las facturas por el ID
        """
        facturas = await db.execute(
            select(FacturaDAO.id)
                .where(FacturaDAO.id_usuario == id)
            )
        facturas = facturas.fetchall()

        if facturas:
            listaLibros = []
            i = 0
            for factura in facturas:
                informacionFactura = await db.execute( 
                    select(FacturaLibroDAO.id_libro, FacturaLibroDAO.estado, FacturaLibroDAO.fecha_fin) 
                    .where(FacturaLibroDAO.id_factura == factura[0]) 
                    ) 
                informacionFactura = informacionFactura.fetchall()
                
                for libro in informacionFactura:
                    ISSNyTienda = await db.execute(
                        select(LibroTiendaDAO.ISSN, LibroTiendaDAO.id_tienda)
                        .where(LibroTiendaDAO.id == libro[0])
                    )

                    ISSNyTienda = ISSNyTienda.fetchall()
                    ISSN = ISSNyTienda[0][0]

                    titulo = await db.execute(
                        select(LibroDAO.titulo)
                        .where(LibroDAO.ISSN == ISSN)
                    )

                    titulo = titulo.fetchall()
                    titulo = titulo[0][0]

                    nombreTienda = await db.execute(
                        select(TiendaDAO.nombre)
                        .where(TiendaDAO.id == ISSNyTienda[0][1])
                    )

                    nombreTienda = nombreTienda.fetchall()
                    nombreTienda = nombreTienda[0][0]

                    listaLibros.append([i, ISSN, titulo, nombreTienda, libro[1], libro[2]])
                
                i+=1

            return listaLibros
        else:
            return None
        
        
    async def generar_factura(self, userId: str, saldo: int, db: AsyncSession):
        # Crea y añade una nueva factura
        nueva_factura = FacturaDAO(
            id_usuario=userId,
            fecha=date.today(),
            total=saldo
        )
        db.add(nueva_factura)

        # Hacer un commit para asegurar que la factura se guarda en la base de datos
        await db.commit()

    
    async def generar_factura_libro(self, idFactura, idBook, estadoEnvio, db: AsyncSession):

        idBook = idBook[0]

        db.add( FacturaLibroDAO(
            id_factura = idFactura,
            id_libro = idBook,
            estado = int(estadoEnvio)
            )
        )        

        await db.commit()

    async def buscarFacturaGenerada(self, userId, saldo, db: AsyncSession):

        idFactura = await db.execute(
            select(FacturaDAO.id)
            .where(
                FacturaDAO.id_usuario == str(userId),
                FacturaDAO.fecha == date.today(),
                FacturaDAO.total == int(saldo)
            )
        )

        idFactura = idFactura.first()
        idFactura = idFactura[0]
        
        return idFactura

    async def borrarReservas(self, userId, db: AsyncSession):
        await db.execute(
            delete(ReservaDAO)
            .where(ReservaDAO.id_usuario == userId)
        )
        await db.commit()

    async def generate_registro_devolucion(self, userId, db: AsyncSession):
        
        result = '1'
        while result is not None:
            codigo = await self.generate_recovery_code()
            codigo = int(codigo)


            result = await db.execute(
            select(CodigoDevolucionDAO.id)
            .where(CodigoDevolucionDAO.id == codigo)
            )
            
            result = result.scalars().first()

        db.add( CodigoDevolucionDAO(
            id = codigo,
            id_usuario = userId,
            fecha_fin = datetime.now()
            )
        )        

        await db.commit()

        return codigo
    
    async def generate_registro_librosADevolver(self, codigo, book, db: AsyncSession):

        db.add( LibrosDevolucionDAO(
            codigo_devolucion = codigo,
            id_libro = book
            )
        )        

        await db.commit()

    async def depurar_devoluciones(self, db: AsyncSession):
        result = await db.execute(
            select(CodigoDevolucionDAO.id)
            .where(CodigoDevolucionDAO.fecha_fin < datetime.now().date() - timedelta(days=3))
        )

        ids = [row[0] for row in result.fetchall()]

        for id in ids:
            await db.execute(
                delete(LibrosDevolucionDAO)
                .where(LibrosDevolucionDAO.codigo_devolucion == id)
            )
            
            await db.execute(
                delete(CodigoDevolucionDAO)
                .where(CodigoDevolucionDAO.id == id)
            )
            
        await db.commit()        

    async def books_by_devolutionCode(self, codigo, db: AsyncSession):
        
        issn_list = await db.execute(
                select(LibrosDevolucionDAO.id_libro)
                .where(LibrosDevolucionDAO.codigo_devolucion == int(codigo))
            )
        
        return [row[0] for row in issn_list.fetchall()]
    
    async def users_by_devolutionCode(self, codigo, db: AsyncSession):
        
        user = await db.execute(
                select(CodigoDevolucionDAO.id_usuario)
                .where(CodigoDevolucionDAO.id == int(codigo))
            )
        
        return user.first()[0]
    
    async def shopID_by_shopName(self, shopName, db: AsyncSession):
        
        shopId = await db.execute(
                select(TiendaDAO.id)
                .where(TiendaDAO.nombre == shopName)
            )
        
        return shopId.first()[0]
    
    async def changeBookState(self, userId, ISSN, db: AsyncSession):
        
        stmt = select(FacturaLibroDAO.id).\
            join(FacturaDAO).\
            join(LibroTiendaDAO).\
            where(
                FacturaDAO.id_usuario == userId,
                LibroTiendaDAO.ISSN == ISSN
            )

        # Ejecutar la consulta y obtener el ID de la factura-libro
        result = await db.execute(stmt)
        factura_libro_id = result.scalar()

        # Actualizar el estado del libro usando el ID obtenido
        await db.execute(
            update(FacturaLibroDAO).
            where(FacturaLibroDAO.id == factura_libro_id).
            values(estado=5)
        )

        # Hacer commit de la transacción
        await db.commit()

    async def return_money(self, userId, dinero, db: AsyncSession):
        await db.execute(
            update(UsuarioDAO)
            .where(UsuarioDAO.DNI == userId)
            .values(saldo = UsuarioDAO.saldo + dinero)
        )

        await db.commit()