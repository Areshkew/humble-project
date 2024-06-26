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
import re


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
        self.route.add_api_route("/personal/{id}", self.book_personal_information, methods=["GET"])
        self.route.add_api_route("/multiple-personal/{list_issn}", self.book_multiple_personal_information, methods=["GET"])
        self.route.add_api_route("/multiple/{list_issn}", self.book_multiple_information, methods=["GET"])
        self.route.add_api_route("/reservar/{issn_con_tienda}", self.book_solicitar_reservas, methods=["POST"])
        self.route.add_api_route("/obtener-reservas/{id}", self.book_obtener_reservas, methods=["GET"])
        self.route.add_api_route("/cancelar-reserva/{body}", self.book_cancelar_reservas, methods=["POST"])
        self.route.add_api_route("/entregarTodos", self.book_entregar_envios, methods=["POST"])
    
    async def search_books(self, q: str = Query(..., min_length=3, max_length=50), db: Session = Depends(get_db_session)):
        books = await self.bookservice.book_search(db, q)
        
        if books:
            return {"success": True, "results": books}
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No se encontraron resultados.")
    

    async def explore_books(self, page: int = 1, size: int = 15, category: str = None, min_price: int = None, max_price: int = None, 
                        price_order: str = None, start_date: str = None, end_date: str = None, year_filter: int = None,state: bool = None, language: str = None, min_page: int = None, max_page: int = None,
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

        if year_filter is not None and start_date is None and end_date is None:
            start_date = f"{year_filter}-01-01"
            end_date = f"{year_filter}-12-31"


        if category is not None:
            category = generos_dict.get(category)
            if category is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El genero solicitado no es valido")

        filters = {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "price_order": price_order,
            "price_order": price_order,
            "start_date": start_date,
            "end_date": end_date,
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

        if "portada" in data and data["portada"]:
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
    
    async def book_personal_information(self, id: str, db: Session = Depends(get_db_session)):

        book_personal_info = await self.bookservice.get_personal_information(db, id)
        if book_personal_info:
            return book_personal_info
        else:
            raise HTTPException(status_code=404, detail="No existen unidades registradas del Libro")

    async def book_multiple_information(self, list_issn: str, db: Session = Depends(get_db_session)):
        issn_list = list_issn.split(',')
        books_information = []

        for id in issn_list:
            book_info = await self.bookservice.get_information(db, id)
            if book_info and await self.bookservice.get_personal_information(db, book_info['ISSN']) != []:
                book_info.pop('resenia')
                books_information.append(book_info)

        if books_information:
            return books_information
        else:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        
    async def book_multiple_personal_information(self, list_issn: str, db: Session = Depends(get_db_session)):
        issn_list = list_issn.split(',')
        books_information = {}
        

        for issn in issn_list:
            book_personal_info = await self.bookservice.get_personal_information(db, issn)
            personal_information = []

            if book_personal_info:
                for book in book_personal_info:
                    for i in range(0,book['cantidad']):
                        personal_information.append(str(issn)+ "-"+ str(i+1) + " en "+ book['tienda'])

                books_information[issn] = personal_information
            else:
                return 0

        if books_information:
            return books_information
        else:
            raise HTTPException(status_code=404, detail="No existen unidades registradas del Libro")
        
    async def book_solicitar_reservas(self, issn_con_tienda: str, db: Session = Depends(get_db_session)):
        '''
        Valida y revisa que es posible hacer la reserva, por medio de:
        - Validar la existencia del libro
        - Validar que en total no pueda tener más de 5 reservas
        - Validar que no pueda reservar más de 3 veces el mismo libro
        '''

        #Se depura las consultas
        issn_tienda_list = issn_con_tienda.split(',')

        userId = issn_tienda_list[0]
        issn_tienda_list = issn_tienda_list[1:]

        listaReservas = []
        for issnYTienda in issn_tienda_list:
            issnComaTienda = re.sub(r'-.* en ', ',', issnYTienda)
            partes = issnComaTienda.split(',')
            listaReservas.append({'ISSN': partes[0], 'Lib': partes[1]})

        #Borrar reservas que ya no estén vigentes
        await self.bookservice.depure_reservations(db)

        #Verificar existencias
        personal_information = await self.book_multiple_personal_information(','.join([result['ISSN'] for result in listaReservas]), db)
        for key in personal_information.keys():
            if personal_information[key] == []:
                raise HTTPException(status_code=404, detail=f"No existen unidades de {key}")
        
        #Verificar que no haya más reservas
        reservasVigentes = await self.bookservice.user_reservations(db, userId)

        if len(reservasVigentes) + len(listaReservas) > 5:
            raise HTTPException(status_code=404, detail=f"Ya tienes {len(reservasVigentes)} libros reservados, no se pueden reservar más de 5")
        else:
            issn = []
            for result in listaReservas:
                issn.append(result['ISSN'])
            issn2 = []
            for result in reservasVigentes:
                issn2.append(result['id_libro'])
            
            conteos = {}
            for reserva in issn2 + issn:
                if reserva in conteos:
                    if conteos[reserva]>=3:
                        raise HTTPException(status_code=404, detail="No se pueden reservar más de 3 veces el mismo ejemplar")
                    else:
                        conteos[reserva] += 1
                else:
                    conteos[reserva] = 1

        for reserva in listaReservas:
            if await self.bookservice.new_reservation(db,userId, reserva) == False:
                raise HTTPException(status_code=404, detail=f"No existen libros disponibles en {reserva['Lib']}")
            
        return {"detail": "Se realizó la reserva correctamente", "success": True}

    async def book_obtener_reservas(self, id: str, db: Session = Depends(get_db_session)):
        #Borrar reservas que ya no estén vigentes
        await self.bookservice.depure_reservations(db)

        return await self.bookservice.user_reservations(db, id)
    
    async def book_cancelar_reservas(self, body: str, db: Session = Depends(get_db_session)):
        body = body.split(',')
        userId = body[0]
        ISSN = body[1]
        fecha = body[2]
        tienda = body[3]

        await self.bookservice.depure_reservations(db)

        if userId and ISSN and fecha and tienda:
            return await self.bookservice.cancelate_reservation(db, userId, ISSN, fecha, tienda)
        else:
            raise HTTPException(status_code=404, detail=f"No se tienen todos los datos para cancelar")
            

    async def book_entregar_envios(self, db: Session =  Depends(get_db_session)):
        await self.bookservice.marcarTodosLosEnviosComoEntregados(db)
