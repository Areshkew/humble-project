import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm

from app.repositories.models import LibroTiendaDAO, TiendaDAO, LibroDAO
from db.connection import engine

# Función principal
async def main():
    await add_books_to_stores()

# Función para agregar libros a las tiendas
async def add_books_to_stores():
    async with AsyncSession(engine) as session:
        try:
            # Obtener todas las tiendas
            tiendas_result = await session.execute(select(TiendaDAO))
            tiendas = tiendas_result.scalars().all()

            if not tiendas:
                print("No hay tiendas disponibles en la base de datos.")
                return

            # Obtener todos los libros
            libros_result = await session.execute(select(LibroDAO))
            libros = libros_result.scalars().all()

            if not libros:
                print("No hay libros disponibles en la base de datos.")
                return

            # Obtener todas las relaciones libro-tienda existentes
            libro_tienda_result = await session.execute(select(LibroTiendaDAO))
            libro_tienda_existentes = libro_tienda_result.scalars().all()

            libro_tienda_dict = {(lt.id_tienda, lt.ISSN): lt for lt in libro_tienda_existentes}

            new_entries = []
            for libro in tqdm(libros, desc="Assigning books to stores", unit="book"):
                for tienda in tiendas:
                    cantidad = random.randint(1, 100)  # Cantidad aleatoria entre 1 y 100
                    key = (tienda.id, libro.ISSN)

                    if key in libro_tienda_dict:
                        libro_tienda_dict[key].cantidad += cantidad
                    else:
                        new_entries.append(LibroTiendaDAO(
                            id_tienda=tienda.id,
                            ISSN=libro.ISSN,
                            cantidad=cantidad
                        ))

            # Insertar las nuevas entradas en bloque
            session.add_all(new_entries)

            # Confirmar los cambios
            await session.commit()
            print("Libros agregados correctamente a las tiendas en la base de datos.")
        except IntegrityError as e:
            await session.rollback()
            print(f"Error al agregar los libros a las tiendas en la base de datos: {e}")
        finally:
            await session.close()

# Ejecutar el script principal
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
