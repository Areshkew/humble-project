# Humble Project - Backend

Este repositorio contiene el backend del sistema Humble, una plataforma avanzada para la gestión de librerías en línea. El backend está diseñado para manejar la autenticación de usuarios, la gestión de bases de datos y la lógica del servidor.

## Instrucciones de Configuración

### 1. Configuración del Archivo `.env`

Asegúrate de que el archivo `.env` en la raíz del proyecto contenga los datos correctos para la conexión a la base de datos. Este archivo debe incluir las siguientes variables de entorno:

- `DB_NAME`: Nombre de la base de datos PostgreSQL.
- `DB_USER`: Usuario de la base de datos.
- `DB_PASSWORD`: Contraseña del usuario.
- `DB_HOST`: Host de la base de datos.
- `DB_PORT`: Puerto de conexión de la base de datos.

Modifica estos valores según tus necesidades y asegúrate de que coincidan con tu configuración de PostgreSQL.

### 2. Instalación de Dependencias

Instala los paquetes requeridos en tu entorno de Python utilizando el siguiente comando:

```bash
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias especificadas en el archivo `requirements.txt`.

### 3. Configuración de la Carpeta de Imágenes

Verifica que la carpeta `images` exista en la raíz del proyecto. Esta carpeta se utilizará para almacenar las imágenes de los libros.

### 4. Ejecución del Servidor

Inicia el servidor ejecutando el archivo `main.py` con el siguiente comando:

```bash
python main.py
```

Este comando lanzará el backend y estará listo para recibir peticiones.

## Programas Necesarios y Dependencias

### PostgreSQL

- **Requisito:** PostgreSQL debe estar instalado en tu sistema.
- **Descarga:** Puedes obtener PostgreSQL desde su [página oficial](https://www.postgresql.org/download/).
- **Configuración:** Después de la instalación, crea una base de datos con el nombre especificado en `DB_NAME` en el archivo `.env`.

### Llaves RSA para JWT

Para la autenticación basada en JWT, necesitas generar una llave RSA pública y privada:

- **Generador de Llaves:** Utiliza un generador como [Cryptotools RSA Generator](https://cryptotools.net/rsagen).
- **Ubicación de las Llaves:** Guarda las llaves en la carpeta `keys` con los nombres `private_key.pem` y `public_key.pem`.

## Uso de Scripts

### Script de Población de Libros

El script `book_population_script.py` se utiliza para poblar la base de datos con datos de libros desde archivos JSON. Sigue estos pasos para usarlo:

1. **Preparación del Directorio JSON:**
   - Crea una carpeta llamada `json` dentro del directorio `scripts`.
   - Coloca los archivos JSON en esta carpeta. Estos archivos contendrán la información de los libros a poblar en la base de datos.

2. **Ejecución del Script:**
   - Desde la raíz del proyecto, ejecuta el script como un módulo con el siguiente comando:
     ```bash
     python -m scripts.book_population_script
     ```
   - Este comando asegurará que el script se ejecute correctamente y que los datos se inserten en la base de datos según lo especificado.

### Script de Población de Unidades de Libros en Tiendas

El script `populate_stores_script.py` se utiliza para asignar cantidades aleatorias de libros a cada tienda registrada en el sistema. Esto es útil para simular inventarios en diferentes puntos de venta. A continuación, se describen los pasos para usar este script:

1. **Preparación del Entorno:**
   - Asegúrate de que la base de datos esté correctamente poblada con las tiendas y los libros usando los scripts previos o manualmente a través de la interfaz de administración.

2. **Ejecución del Script:**
   - Desde la raíz del proyecto, ejecuta el script como un módulo con el siguiente comando:
     ```bash
     python -m scripts.populate_stores_script
     ```
   - Este comando generará y asignará cantidades aleatorias de cada libro a las tiendas registradas en el sistema, actualizando así el inventario disponible en cada tienda.

3. **Verificación:**
   - Tras la ejecución del script, verifica que las cantidades de los libros en cada tienda se hayan actualizado correctamente. Esto se puede revisar a través de la base de datos o mediante las interfaces de consulta del sistema.

---

Para más información y preguntas sobre la configuración o el uso del backend del Proyecto Humble, no dudes en abrir un "issue" en este repositorio.

[Repositorio del FrontEnd](https://github.com/Areshkew/humble-project-ui)
