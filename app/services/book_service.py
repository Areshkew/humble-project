from app.repositories.book_dao import LibroDAO
from app.utils.class_utils import Injectable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

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
            