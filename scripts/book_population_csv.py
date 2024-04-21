from app.repositories.models import *
from datetime import datetime
from db.connection import engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random, asyncio, csv, tempfile, subprocess, os, time
from sqlalchemy.orm import sessionmaker

# Conexión DB
AsyncSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Cache para almacenar las editoriales.
publishing_cache = {}

# OPERACIONES DE BASE DATOS
async def load_genre_mapping():
    """ Cargar generos de la db. """
    genre_map = {}
    async with AsyncSession() as session:
        result = await session.execute(select(GeneroDAO))
        genre_map = {genre.genero: genre.id for genre in result.scalars()}
    return genre_map

async def load_publishing_mapping():
    """ Cargar generos de la db. """
    global publishing_cache
    async with AsyncSession() as session:
        result = await session.execute(select(EditorialDAO))
        publishing_cache = {publishing.editorial: publishing.id for publishing in result.scalars()}
           
async def upload_data(data_path, table_name, columns):
    """ Subir datos con la utilidad \copy de psql, es necesario tener el binario en las variables de entorno para su uso. """
    os.environ['PGPASSWORD'] = os.getenv("DB_PASSWORD")
    async with AsyncSession() as session:
        try:
            cmd = (
                f"psql -c \"\\copy {table_name} ({','.join(columns)}) FROM '{data_path}' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')\" "
                f"-h {session.bind.url.host} -U {session.bind.url.username} -d {session.bind.url.database}"
            )
            result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
            print(f"Data loaded successfully to {table_name}: ", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error loading data to {table_name}: {e.stderr}")


# PREPARACIÓN DE DATOS
async def prepare_publishing_data(input_file):
    """
    Preparar datos de editoriales para ser agregados en la base de datos, en un archivo csv temporal. 
    """
    temp_file = tempfile.NamedTemporaryFile(mode='w+', newline='', delete=False, encoding='utf-8')
    seen_publishers = set()  # Revisar editoriales repetidas

    with open(input_file, mode='r', encoding='utf-8') as infile, temp_file as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['editorial']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            publisher = row.get('detalles/editorial', 'desconocido').strip()

            if not publisher:  # Editoriales sin nombre o nulas
                publisher = "desconocido"

            if publisher not in seen_publishers:
                writer.writerow({'editorial': publisher})
                seen_publishers.add(publisher)

    return temp_file.name

async def prepare_genre_relationships(books_data):
    """ Preparar datos de generos de cada libro para ser agregados en la base de datos, en un archivo csv temporal.  """
    temp_file = tempfile.NamedTemporaryFile(mode='w+', newline='', delete=False, encoding='utf-8')
    with open(temp_file.name, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['ISSN', 'id_genero'])
        writer.writeheader()
        for book in books_data:
            if 'ISSN' in book and 'genero' in book:
                writer.writerow({'ISSN': book['ISSN'], 'id_genero': book['genero']})
    return temp_file.name

async def prepare_data_file_and_dict(input_file, column_mapping, genre_map):
    """ Preparar datos de libros para ser agregados en la base de datos, en un archivo csv temporal. """
    global publishing_cache
    dias_por_mes = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }

    # Rear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(mode='w+', newline='', delete=False, encoding='utf-8')
    all_data = []  # Almacenamiento de todos los registros

    with open(input_file, mode='r', encoding='utf-8') as infile, temp_file as outfile:
        reader = csv.DictReader(infile)
        fieldnames = [column_mapping[field] for field in reader.fieldnames if field in column_mapping and field != 'detalles/genero']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            genero_value = genre_map.get(row['detalles/genero'], row['detalles/genero'])
            row = {column_mapping.get(key, key): value for key, value in row.items() if column_mapping.get(key, key) in fieldnames}
            
            row['estado'] = True if row['estado'] == 'Nuevo' else False

            if not row['editorial']:
                row['editorial'] = 'desconocido'

            row['editorial'] = publishing_cache[ row['editorial'] ]

            if not row['num_paginas']:
                row['num_paginas'] = random.randint(50, 500)

            if not row['fecha_publicacion']:
                row['fecha_publicacion'] = random.randint(1900, 2020)

            if not row['idioma']:
                row['idioma'] = "desconocido"
            
            if not row['autor']:
                row['autor'] = "desconocido"

            mes = random.randint(1, 12)
            dia = random.randint(1, dias_por_mes[mes])

            # Fecha
            fecha_publicacion_str = f"{dia}-{mes}-{row['fecha_publicacion']}"
            row['fecha_publicacion'] = datetime.strptime(fecha_publicacion_str, '%d-%m-%Y').date()

            writer.writerow(row)

            row['genero'] = genero_value # Ignoramos el genero en el archivo, pero es agregado en los datos.
            all_data.append(row)

    return temp_file.name, all_data

async def main():
    input_file = './scripts/json/books.csv'
    column_mapping = {'detalles/ISBN': 'ISSN', 
                      'detalles/titulo': 'titulo',
                      'detalles/autor': 'autor',
                      'detalles/resena': 'resenia',
                      'detalles/paginas': 'num_paginas',
                      'detalles/idioma': 'idioma',
                      'detalles/ano_publicacion': 'fecha_publicacion',
                      'detalles/estado': 'estado',
                      'detalles/img': 'portada',
                      'precios/PrecioAntes': 'precio',
                      'precios/PrecioAhora': 'descuento',
                      'detalles/editorial': 'editorial',
                      'detalles/genero': 'genero',
                    }
    
    print("Uploading Publishings...")
    publishing_data_path = await prepare_publishing_data(input_file)
    await upload_data(publishing_data_path, 'editoriales', ['editorial'])

    print("Uploading Books...")
    await load_publishing_mapping()
    genre_map = await load_genre_mapping()
    data_path, data = await prepare_data_file_and_dict(input_file, column_mapping, genre_map)
    await upload_data(data_path, 'libros', [
        'titulo', 'autor', 'editorial', 'fecha_publicacion', 'idioma', 'num_paginas',
        '\\\"ISSN\\\"', 'portada', 'resenia', 'estado', 'precio', 'descuento'
    ])

    print("Uploading book Genres...")
    genre_file_path = await prepare_genre_relationships(data)
    await upload_data(genre_file_path, 'libros_genero', ['\\\"ISSN\\\"', 'id_genero'])

if __name__ == "__main__":
    asyncio.run(main())