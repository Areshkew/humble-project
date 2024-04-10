import json

from app.repositories.models import *

from db.connection import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import random


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


async def main():
    # Llamada a la función
    file_path = './scripts/json/books.json'
    data = read_json(file_path)
    await add_books_to_database(data)


async def add_books_to_database(books_data):
    async with AsyncSession(engine) as session:
        try:
            for book_data in books_data:


                editorial_name = book_data['detalles']['editorial']
                
                # Buscar la editorial en la base de datos
                editorialbd = await session.execute(EditorialDAO.__table__.select().where(EditorialDAO.editorial == editorial_name))
                editorialbd = editorialbd.scalar_one_or_none()

                if editorialbd is None:
                    # Si no existe, crearla
                    new_editorial = EditorialDAO(editorial=editorial_name)
                    session.add(new_editorial)
                    await session.flush()  # Para obtener el ID de la nueva editorial
                    editorial_id = new_editorial.id
                else:
                    editorial_id = editorialbd


                #Para el estado dar el valor booleano segun que es(0: Nuevo, 1: Usado)
                estado = 0 if book_data['detalles']['estado'] == 'nuevo' else 1


                #Para obtener el año de publicacion
                ano_publicacion = book_data['detalles']['ano_publicacion']

                dias_por_mes = { #Dias que tiene cada mes para luego hacer el random
                        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
                    }
                
                if not ano_publicacion:
                    ano_publicacion = random.randint(1900, 2020)
                    mes = random.randint(1, 12)
                    dia = random.randint(1, dias_por_mes[mes])
                else:
                    mes = random.randint(1, 12)
                    dia = random.randint(1, dias_por_mes[mes])

                #Para construir la fecha de publicación
                fecha_publicacion_str = f"{dia}-{mes}-{ano_publicacion}"
                fecha = datetime.strptime(fecha_publicacion_str, '%d-%m-%Y').date()


                #Asignar valor random a paginas si es vacio
                paginas = book_data['detalles']['paginas']

                if not paginas:
                    paginas = random.randint(50, 500)
                else:
                   pass


                book = LibroDAO(
                    ISSN=book_data['detalles']['ISBN'],
                    titulo=book_data['detalles']['titulo'],
                    num_paginas=int(paginas),
                    idioma=book_data['detalles']['idioma'],
                    fecha_publicacion=fecha,
                    estado= estado,
                    portada=book_data['detalles']['img'],
                    precio=float(book_data['precios']['PrecioAhora']),
                    editorial=editorial_id
                )
                session.add(book)


                #Para asignar el libro con su género
                genero_name = book_data['detalles']['genero']
                genero = await session.execute(GeneroDAO.__table__.select().where(GeneroDAO.genero == genero_name))
                genero = genero.first()

                if genero is not None:
                    libro_genero = LibroGeneroDAO(ISSN=book.ISSN, id_genero=genero.id)
                    session.add(libro_genero)


            #Subir cambios a la db
            await session.commit()
            print("Libros agregados correctamente a la base de datos.")
        except IntegrityError as e:
            await session.rollback()
            print(f"Error al agregar los libros a la base de datos: {e}")
        finally:
            await session.close()


# Ejecutar el código principal
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
