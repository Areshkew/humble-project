from app.services.book_service import BookService
from app.utils.class_utils import Injectable, inject
from app.utils.db_utils import get_db_session
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.params import Query
from sqlalchemy.orm import Session

@inject(BookService)
class BookController(Injectable):
    def __init__(self):
        self.route = APIRouter(prefix='/book')
        self.route.add_api_route("/search", self.search_books, methods=["GET"])
        self.route.add_api_route("/getbooks", self.get_books, methods=["GET"])
    
    
    async def search_books(self, q: str = Query(..., min_length=3, max_length=50), db: Session = Depends(get_db_session)):
        books = await self.bookservice.book_search(db, q)
        
        if books:
            return {"success": True, "results": books}
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No se encontraron resultados.")
    

    async def get_books(self, page: int = 1, size: int = 15, category: str = None, min_price: int = None, max_price: int = None, 
                        price_order: str = None, publication_date: str = None, state: bool = None, language: str = None, 
                        db: Session = Depends(get_db_session)):  #price_order = "min_max" or "max_min" #publication_date = YY-MM-DD     
            
        if size > 30:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El tamaño máximo permitido es de 30 libros por página.")
        
        filters = {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "price_order": price_order,
            "publication_date": publication_date,
            "state": state,
            "language": language
        }

        # Llamada al servicio para obtener los libros filtrados
        books, total_pages = await self.bookservice.filter_books(db, filters, page, size)

        if page > total_pages:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de página solicitado excede el número total de páginas.")

        return {"books": books, "total_pages": total_pages}
