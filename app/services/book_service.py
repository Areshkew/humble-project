from app.repositories.book_dao import LibroDAO
from app.repositories.bookgenre_dao import LibroGeneroDAO
from app.repositories.genre_dao import GeneroDAO
from app.repositories.publishing_dao import EditorialDAO
from app.utils.class_utils import Injectable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc
from datetime import datetime

class BookService(Injectable):
    async def book_search(self, db: AsyncSession, query: str):
        """
            Realizar busqueda de libros a través de una query.
        """  
        max_results = 7
        formatted_query = ' & '.join(query.split())
        
        stmt = select(LibroDAO).where(
                    func.to_tsvector("spanish", 
                            func.concat(LibroDAO.titulo) # TODO: Add more fields if necessary.
                        ).bool_op("@@")(
                            func.to_tsquery("spanish", formatted_query)
                        )
                ).limit(max_results)
        
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