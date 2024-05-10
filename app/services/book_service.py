from app.repositories.book_dao import LibroDAO
from app.repositories.bookgenre_dao import LibroGeneroDAO
from app.repositories.genre_dao import GeneroDAO
from app.repositories.publishing_dao import EditorialDAO
from app.utils.class_utils import Injectable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc, delete
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class BookService(Injectable):
    async def book_search(self, db: AsyncSession, query: str, max_results: int = 7):
        """
            Realizar busqueda de libros a través de una query.
        """  
        formatted_query = ' & '.join(query.split())
        
        stmt = select(LibroDAO).where(
                    func.to_tsvector("spanish", 
                            func.concat(LibroDAO.titulo, " ", LibroDAO.autor, " ", LibroDAO.ISSN) # TODO: Add more fields if necessary.
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
            stmt = stmt.where(LibroDAO.precio >= filters["min_price"])

        if filters["max_price"] is not None:
            stmt = stmt.where(LibroDAO.precio <= filters["max_price"])

        # Filtrar por rango de paginas
        if filters["min_page"] is not None:
            stmt = stmt.where(LibroDAO.num_paginas >= filters["min_page"])

        if filters["max_page"] is not None:
            stmt = stmt.where(LibroDAO.num_paginas <= filters["max_page"])

        # Filtrar por fecha de publicación
        if filters["publication_date"] is not None:
            publication_date = datetime.strptime(filters["publication_date"], "%Y-%m-%d").date()
            stmt = stmt.where(LibroDAO.fecha_publicacion == publication_date)

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