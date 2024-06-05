from app.repositories.book_dao import LibroDAO
from app.repositories.bookgenre_dao import LibroGeneroDAO
from app.repositories.genre_dao import GeneroDAO
from app.repositories.publishing_dao import EditorialDAO
from app.repositories.bookshop_dao import LibroTiendaDAO
from app.repositories.shop_dao import TiendaDAO
from app.repositories.reservation_dao import ReservaDAO
from app.repositories.user_dao import UsuarioDAO
from app.repositories.return_books import LibrosDevolucionDAO
from app.repositories.return_code import CodigoDevolucionDAO
from app.utils.class_utils import Injectable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc, update, delete, cast, String, Date
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta

class BookService(Injectable):
    async def book_search(self, db: AsyncSession, query: str, max_results: int = 7):
        """
            Realizar busqueda de libros a través de una query.
        """  
        formatted_query = ' & '.join(query.split())
        
        stmt = select(LibroDAO, EditorialDAO).join(EditorialDAO, LibroDAO.editorial == EditorialDAO.id).where(
                func.to_tsvector("spanish", 
                        func.concat(LibroDAO.titulo, " ", LibroDAO.autor, " ", LibroDAO.ISSN, " ", EditorialDAO.editorial, " ", LibroDAO.precio) # Incluir el nombre de la editorial
                    ).bool_op("@@")(
                        func.to_tsquery("spanish", formatted_query)
                    )
            )
        
        if max_results != -1:
            stmt = stmt.limit(max_results)

        result = await db.execute(stmt)
        books = result.scalars().all()
        
        if books:
            books_list = [{key: value for key, value in book.__dict__.items() if not key.startswith('_')} for book in books]
            return books_list
        
        return None
            
    async def filter_books(self, db: AsyncSession, filters: dict, page: int, size: int):
        """
        Obtener libros filtrados según los parámetros proporcionados y paginado.
        """
        stmt = select(LibroDAO)

        # Nombre de editorial
        stmt = select(LibroDAO, EditorialDAO.editorial).join(EditorialDAO, LibroDAO.editorial == EditorialDAO.id)

        # Filtrar por género
        if filters["category"] is not None:
            genre = await db.execute(select(GeneroDAO.id).where(GeneroDAO.genero == filters["category"]))
            genre_id = genre.scalar()
            if genre_id is not None:
                stmt = stmt.join(LibroGeneroDAO).where(LibroGeneroDAO.id_genero == genre_id)

        # Filtrar por rango de precios
        if filters["min_price"] is not None:
            stmt = stmt.where(LibroDAO.descuento >= filters["min_price"])

        if filters["max_price"] is not None:
            stmt = stmt.where(LibroDAO.descuento <= filters["max_price"])

        # Filtrar por rango de paginas
        if filters["min_page"] is not None:
            stmt = stmt.where(LibroDAO.num_paginas >= filters["min_page"])

        if filters["max_page"] is not None:
            stmt = stmt.where(LibroDAO.num_paginas <= filters["max_page"])

         # Filtrar por rango de fecha de publicación
        if filters["start_date"] is not None and filters["end_date"] is not None:
            start_date = datetime.strptime(filters["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(filters["end_date"], "%Y-%m-%d").date()
            stmt = stmt.where(LibroDAO.fecha_publicacion.between(start_date, end_date))



            
        # Filtrar por estado
        if filters["state"] is not None:
            stmt = stmt.where(LibroDAO.estado == filters["state"])

        # Filtrar por idioma
        if filters["language"] is not None:
            stmt = stmt.where(LibroDAO.idioma == filters["language"])

        #Filtrar orden de precio
        if filters["price_order"] == "min_max":
            stmt = stmt.order_by(asc(LibroDAO.precio))
        elif filters["price_order"] == "max_min":
            stmt = stmt.order_by(desc(LibroDAO.precio))


        # Obtener el número total de libros sin paginación
        total_books_stmt = select(func.count()).select_from(stmt.alias())
        total_books_result = await db.execute(total_books_stmt)
        total_books = total_books_result.scalar()

        # Calcular el número total de páginas
        total_pages = (total_books + size - 1) // size


        # Aplicar paginación
        offset = (page - 1) * size
        stmt = stmt.limit(size).offset(offset)

        # Busqueda del stmt normal
        result = await db.execute(stmt)
        books = result.fetchall()

        if books:
            books_list = []
            for book, editorial_name in books:
                book_dict = {key: value for key, value in book.__dict__.items()}
                book_dict["editorial"] = editorial_name
                books_list.append(book_dict)
            return books_list, total_pages
            
        return None, total_pages
    
    
    async def get_information(self, db: AsyncSession, id: str):
        """
        Obtener toda la información de un libro por su ID.
        """

        book = await db.get(LibroDAO, id)

        if book:
            # Obtener el nombre de la editorial
            editorial_name = await db.scalar(select(EditorialDAO.editorial).where(EditorialDAO.id == book.editorial))

            # Obtener el nombre del género del libro
            genre_name = await db.scalar(select(GeneroDAO.genero).join(LibroGeneroDAO).where(LibroGeneroDAO.ISSN == id))

            book_info = {
                "ISSN": book.ISSN,
                "titulo": book.titulo,
                "autor": book.autor,
                "resenia": book.resenia,
                "num_paginas": book.num_paginas,
                "idioma": book.idioma,
                "fecha_publicacion": book.fecha_publicacion,
                "estado": book.estado,
                "portada": book.portada,
                "precio": book.precio,
                "descuento": book.descuento,
                "editorial": editorial_name,
                "genero": genre_name
            }

            return book_info
        else:
            return None

    async def delete_books(self, db: AsyncSession, issn_list: list):
        """
            Borrar libros basado en una lista de ISSN. 
        """
        stmt = delete(LibroDAO).where(LibroDAO.ISSN.in_(issn_list))
        result = await db.execute(stmt)
        
        await db.commit()
        return result.rowcount 
    
    async def book_exists(self, db: AsyncSession, ISSN: str) -> bool:
        """
            Verifica si existe una cuenta con el mismo nombre de usuario, correo electrónico o DNI.
        """
        stmt = select(
            LibroDAO.ISSN,
        ).where(
            LibroDAO.ISSN == ISSN
        )
        result = await db.execute(stmt)
        book = result.first()
    
        return book is not None
    
    async def create_book(self, db: AsyncSession, book_data: dict):
        """
        Crear un nuevo libro en la base de datos.
        """
        # 
        editorial_name = book_data.get('editorial')

        # Buscar editorial
        editorial_query = select(EditorialDAO).where(EditorialDAO.editorial == editorial_name)
        editorial_result = await db.execute(editorial_query)
        editorial = editorial_result.scalars().first()

        if not editorial:
            new_editorial = EditorialDAO(editorial=editorial_name)
            db.add(new_editorial)
            await db.commit()
            await db.refresh(new_editorial)
            editorial_id = new_editorial.id
        else:
            editorial_id = editorial.id

        # Remover genero del diccionario y almacenarlo.
        genre_id = book_data.pop('genero', None)

        # 
        book_data['editorial'] = editorial_id
        new_book = LibroDAO(**book_data)

        try:
            db.add(new_book)
            await db.commit()
            await db.refresh(new_book)

            # Después que el libro es creado manejar creación de genero
            if genre_id is not None:
                new_libro_genero = LibroGeneroDAO(id_genero=genre_id, ISSN=new_book.ISSN)
                db.add(new_libro_genero)
                await db.commit()

            return True
        except IntegrityError:
            await db.rollback()
            return None
    
    async def update_book(self, book_data: dict, ISSN: str, db: AsyncSession):
        book = await db.get(LibroDAO, ISSN)

        if "editorial" in book_data:
            editorial_name = book_data.get('editorial')

            # Buscar editorial
            editorial_query = select(EditorialDAO).where(EditorialDAO.editorial == editorial_name)
            editorial_result = await db.execute(editorial_query)
            editorial = editorial_result.scalars().first()

            if not editorial:
                new_editorial = EditorialDAO(editorial=editorial_name)
                db.add(new_editorial)
                await db.commit()
                await db.refresh(new_editorial)
                editorial_id = new_editorial.id
            else:
                editorial_id = editorial.id
            # 
            book_data['editorial'] = editorial_id

        # Remover genero del diccionario y almacenarlo.
        genre_id = book_data.pop('genero', None)

        try:
            for key, value in book_data.items():
                setattr(book, key, value)

            if genre_id is not None:
                libro_genero = await db.execute(select(LibroGeneroDAO).filter(LibroGeneroDAO.ISSN == ISSN))
                libro_genero = libro_genero.scalars().first()
                libro_genero.id_genero = genre_id
                
            await db.commit()

        except IntegrityError:
            await db.rollback()
            return None
    
    async def get_personal_information(self, db: AsyncSession, id: str):
        """
        Obtener toda la información PERSONAL de un libro por su ID.
        """
        
        book_in_store = await db.execute(
            select(TiendaDAO.id, LibroTiendaDAO.cantidad)
            .join(TiendaDAO)
            .filter(LibroTiendaDAO.ISSN == id)
        )
        
        book_store_info_list = []

        if book_in_store:
            for tienda_id, cantidad in book_in_store: 
                
                tienda = await db.scalar(select(TiendaDAO.nombre).where(TiendaDAO.id == tienda_id))

                book_info = {
                    "tienda": tienda,
                    "cantidad": cantidad
                }

                book_store_info_list.append(book_info)
            
            return book_store_info_list
        else:
            return None

    async def user_reservations(self, db: AsyncSession, userId: str):
        stmt = select(
            ReservaDAO.id_libro,
            TiendaDAO.nombre,
            ReservaDAO.fecha_fin
        ).join(TiendaDAO, ReservaDAO.id_tienda == TiendaDAO.id).filter(
            ReservaDAO.id_usuario == userId
        )

        result = await db.execute(stmt)
        result = result.fetchall()

        reservations = [
            {
                "id_libro": row[0],
                "nombre_tienda": row[1],
                "fecha_fin": row[2].isoformat()  # Convertir la fecha a string
            }
            for row in result
        ]

        return reservations
    
    async def depure_reservations(self, db: AsyncSession):
        today = date.today()
    
        # Crear la consulta para eliminar las reservas con fecha_fin menor a hoy
        results = await db.execute(select(ReservaDAO.id_tienda, ReservaDAO.id_libro).filter(ReservaDAO.fecha_fin < today))
        results = results.fetchall()
        for result in results:
            await db.execute(
                update(LibroTiendaDAO)
                .where(LibroTiendaDAO.id_tienda == result[0], LibroTiendaDAO.ISSN == result[1])
                .values(cantidad=LibroTiendaDAO.cantidad + 1)
            )
        await db.execute(delete(ReservaDAO).where(ReservaDAO.fecha_fin < today))
        await db.commit()

    async def new_reservation(self, db: AsyncSession, userId, reserva):
        issn_libro = reserva['ISSN']
        libreria = reserva['Lib']

        lib_id = await db.execute(
                select(TiendaDAO.id)
                .where(TiendaDAO.nombre == libreria)
            )

        lib_id = lib_id.first()[0]

        print(1)
        cantidadLibrosDisponibles = await db.execute(
                select(LibroTiendaDAO.cantidad)
                .where(
                    (LibroTiendaDAO.id_tienda == lib_id) & 
                    (LibroTiendaDAO.ISSN == issn_libro)
                )
            )
        cantidadLibrosDisponibles = cantidadLibrosDisponibles.first()[0]
        print(2)
        if cantidadLibrosDisponibles > 0:
            print(3)
            await db.execute(
                update(LibroTiendaDAO)
                .where(
                    (LibroTiendaDAO.id_tienda == lib_id) & 
                    (LibroTiendaDAO.ISSN == issn_libro)
                )
                .values(cantidad=LibroTiendaDAO.cantidad - 1)
            )
            print(4)
            nuevaReserva = ReservaDAO(
                id_usuario = userId,
                id_libro = issn_libro,
                id_tienda = lib_id,
                fecha_fin = date.today() + timedelta(days=1)
            )

            # Añadir la nueva reserva a la sesión
            db.add(nuevaReserva)
            await db.commit()
            await db.refresh(nuevaReserva)
            
            return True
        else:
            return False
        
    async def cancelate_reservation(self, db: AsyncSession, userId, ISSN, fecha, tienda):
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()

        id_tienda = await db.execute(
            select(TiendaDAO.id)
            .where(TiendaDAO.nombre == tienda)
        )
        id_tienda = id_tienda.fetchall()[0][0]

        reserva = await db.execute(
            select(ReservaDAO)
            .where(
                cast(ReservaDAO.id_usuario, String) == str(userId),
                cast(ReservaDAO.id_libro, String) == str(ISSN),
                cast(ReservaDAO.fecha_fin, Date) == fecha_obj,
                cast(ReservaDAO.id_tienda, String) == str(id_tienda)
            )
        )
        reserva = reserva.scalars().first()

        if reserva:
            await db.execute(
                update(LibroTiendaDAO)
                .where(LibroTiendaDAO.id_tienda == id_tienda, LibroTiendaDAO.ISSN == ISSN)
                .values(cantidad=LibroTiendaDAO.cantidad + 1)
            )

            # Elimina la reserva encontrada
            await db.delete(reserva)
            await db.commit()
            return {"status": "success", "message": "Reserva cancelada correctamente."}
        else:
            return {"status": "error", "message": "No se encontró la reserva con los datos proporcionados."}
        
    async def validar_cantidades(self, ISSN, tienda, cantidad, db: AsyncSession):
        id_tienda = await db.execute(
            select(TiendaDAO.id)
            .where(TiendaDAO.nombre == tienda)
        )

        id_tienda = id_tienda.scalar_one()
        
        cantidadBD = await db.execute(
            select(LibroTiendaDAO.cantidad)
            .where(
                LibroTiendaDAO.id_tienda == id_tienda, 
                LibroTiendaDAO.ISSN == ISSN
                   )
        )
        return cantidad > cantidadBD.scalar_one()
    
    async def calcularSaldo(self, issn, db: AsyncSession):
        saldo = await db.execute(
            select(LibroDAO.descuento)
            .where(LibroDAO.ISSN == issn)
            )
        
        return saldo.scalar_one()

    async def realizar_compra(self, userId, issn, tienda, db: AsyncSession):
        id_tienda = await db.execute(
            select(TiendaDAO.id)
            .where(TiendaDAO.nombre == tienda)
        )
        id_tienda = id_tienda.scalar_one()

        #Resta el saldo
        costo = await db.execute(
            select(LibroDAO.descuento)
            .where(LibroDAO.ISSN == issn)
            )
        
        costo = costo.scalar_one()

        await db.execute((
            update(UsuarioDAO)
            .where(UsuarioDAO.DNI == userId)
            .values(saldo=UsuarioDAO.saldo - costo)
            )
        )

        #Resta la cantidad 
        await db.execute((
            update(LibroTiendaDAO)
            .where(LibroTiendaDAO.ISSN == issn,LibroTiendaDAO.id_tienda == id_tienda)
            .values(cantidad=LibroTiendaDAO.cantidad - 1)
            )
        ) 

        idCambiado = await db.execute(
            select(LibroTiendaDAO.id)
            .where(LibroTiendaDAO.ISSN == issn,LibroTiendaDAO.id_tienda == id_tienda)
        )
        await db.commit()
        return idCambiado.first()
    
    async def return_book(self, issn: str, shopID: int, codigoDevolucion: str, db: AsyncSession):
        await db.execute(
            update(LibroTiendaDAO)
            .where((LibroTiendaDAO.ISSN == issn) 
                   & (LibroTiendaDAO.id_tienda == shopID))
            .values(cantidad=LibroTiendaDAO.cantidad + 1)
        )
        await db.commit()

        saldo = await db.execute(
            select(LibroDAO.descuento)
            .where(LibroDAO.ISSN == issn)
        )
        
        await db.execute(
            delete(LibrosDevolucionDAO)
            .where((LibrosDevolucionDAO.codigo_devolucion == int(codigoDevolucion)) 
                   & (LibrosDevolucionDAO.id_libro == issn))
        )

        return saldo.scalar_one_or_none()
    
    async def delete_devolution_code(self, code, db: AsyncSession):
        await db.execute(
            delete(CodigoDevolucionDAO)
            .where(CodigoDevolucionDAO.id == int(code))
        )

        await db.commit()
        