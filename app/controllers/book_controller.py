from mimetypes import guess_extension
import os, base64
from typing import Optional
from app.models.book_model import Book, BookISSNDelete, BookUpdate
from app.services.book_service import BookService
from app.utils.class_utils import Injectable, inject
from app.utils.db_utils import get_db_session
from fastapi import APIRouter, HTTPException, UploadFile, status, Depends, Request
from fastapi.params import Query
from sqlalchemy.orm import Session

@inject(BookService)
class BookController(Injectable):
    def __init__(self):
        self.route = APIRouter(prefix='/book')
        self.route.add_api_route("/search", self.search_books, methods=["GET"])
        self.route.add_api_route("/explore", self.explore_books, methods=["GET"])
        self.route.add_api_route("/{id}", self.book_information, methods=["GET"])
        self.route.add_api_route("/delete-books", self.delete_books, methods=["POST"])
        self.route.add_api_route("/create-book", self.create_book, methods=["POST"])
        self.route.add_api_route("/edit-book/{ISSN}", self.edit_book, methods=["POST"])
    
    
    async def search_books(self, q: str = Query(..., min_length=3, max_length=50), db: Session = Depends(get_db_session)):
        books = await self.bookservice.book_search(db, q)
        
        if books:
            return {"success": True, "results": books}
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No se encontraron resultados.")
    

    async def explore_books(self, page: int = 1, size: int = 15, category: str = None, min_price: int = None, max_price: int = None, 
                        price_order: str = None, publication_date: str = None, state: bool = None, language: str = None, min_page: int = None, max_page: int = None,
                        db: Session = Depends(get_db_session)):  #price_order = "min_max" or "max_min" #publication_date = YY-MM-DD     
            
        if size > 30:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El tamaño máximo permitido es de 30 libros por página.")
        
        if page <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Numero de pagina invalida.")
        
        generos_dict = {
            "arte_y_disenio": "Arte y Diseño",
            "autoayuda_y_desarrollo_personal": "Autoayuda y Desarrollo Personal",
            "biografia_autobiografia": "Biografía/Autobiografía",
            "ciencia": "Ciencia",
            "ciencia_ficcion": "Ciencia Ficción",
            "ciencia_y_naturaleza": "Ciencia y Naturaleza",
            "critica_y_teoria_literaria": "Crítica y Teoría Literaria",
            "deporte_y_aventura": "Deporte y Aventura",
            "educativo_y_didactico": "Educativo y Didáctico",
            "ensayo": "Ensayo",
            "especializado": "Especializado",
            "estilo_de_vida": "Estilo de Vida",
            "ficcion_general": "Ficción General",
            "filosofia_y_espiritualidad": "Filosofía y Espiritualidad",
            "historica": "Histórica",
            "infantil_juvenil": "Infantil/Juvenil",
            "linguistica": "Lingüística",
            "linguistica_y_estudios_de_lengua": "Lingüística y Estudios de Lengua",
            "negocios_y_economia": "Negocios y Economía",
            "novela_grafica_y_comic": "Novela Gráfica y Cómic",
            "salud_y_bienestar": "Salud y Bienestar",
            "sociedad_y_cultura": "Sociedad y Cultura",
            "tecnico_y_cientifico": "Técnico y Científico",
            "thriller_legal": "Thriller Legal",
            "viajes_y_geografia": "Viajes y Geografía"
        }

        if category is not None:
            category = generos_dict.get(category)
            if category is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El genero solicitado no es valido")

        filters = {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "price_order": price_order,
            "publication_date": publication_date,
            "state": state,
            "language": language,
            "min_page": min_page,
            "max_page": max_page
        }

        # Llamada al servicio para obtener los libros filtrados
        books, total_pages = await self.bookservice.filter_books(db, filters, page, size)

        if page > total_pages:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de página solicitado excede el número total de páginas.")

        return {"books": books, "total_pages": total_pages}


    async def book_information(self, id: str, db: Session = Depends(get_db_session)):

        book_info = await self.bookservice.get_information(db, id)

        if book_info:
            return book_info
        else:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        
    async def delete_books(self, request: Request, issn_list: BookISSNDelete, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "root" and request.state.payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario root o admin.")

        issn_list = issn_list.model_dump()
        
        await self.bookservice.delete_books(db, issn_list["issn_list"])

        return {"success": True}
    
    async def create_book(self,
        book_data: Book,
        request: Request,
        db: Session = Depends(get_db_session)
    ):
        book_dict = book_data.model_dump()
        book = await self.bookservice.book_exists(db, book_dict["ISSN"]) 

        if request.state.payload["role"] != "root" and request.state.payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario root o admin.")
        
        if book:
            raise HTTPException(status_code=403, detail="El libro ya existe en la base de datos.")
        
        if not book_dict["descuento"] or book_dict["descuento"] > book_dict["precio"]:
            book_dict["descuento"] = book_dict["precio"]
            
        # 
        image_folder = 'images/uploaded'
        os.makedirs(image_folder, exist_ok=True)
        
        # Extraer MIME type y decodificar
        header, encoded = book_dict['portada'].split(',')
        mime_type = header.split(';')[0].split(':')[1]
        image_data = base64.b64decode(encoded)
        file_extension = guess_extension(mime_type) or '.bin'

        file_path = os.path.join(image_folder, f"{book_dict['ISSN']}{file_extension}")
        book_dict["portada"] = file_path

        # Guardar imagen al sistema de archivos
        with open(file_path, "wb") as file:
            file.write(image_data)

        # Agregar a DB
        await self.bookservice.create_book(db, book_dict)

        return { "Success": True }
        
    async def edit_book(self, ISSN: str, book_data: BookUpdate, request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] not in ["admin", "root"]:
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario admin y root.")
        
        data = book_data.model_dump()
        data = {key: value for key, value in data.items() if value is not None} #Filtrar datos que no sean default

        if data["portada"]:
            image_folder = 'images/uploaded'
            os.makedirs(image_folder, exist_ok=True)
            
            # Extraer MIME type y decodificar
            header, encoded = data['portada'].split(',')
            mime_type = header.split(';')[0].split(':')[1]
            image_data = base64.b64decode(encoded)
            file_extension = guess_extension(mime_type) or '.bin'

            file_path = os.path.join(image_folder, f"{ISSN}{file_extension}")
            data["portada"] = file_path

            # Guardar imagen al sistema de archivos
            with open(file_path, "wb") as file:
                file.write(image_data)
        else:
            data.pop("portada")

        await self.bookservice.update_book(data, ISSN, db)
        return {"detail": "Se actualizo el libro correctamente.", "success": True}