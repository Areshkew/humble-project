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

## Stack Tecnológico

### Backend: Python con FastAPI

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0%2B-green?style=for-the-badge&logo=fastapi)

El backend del Proyecto Humble está desarrollado en Python utilizando el framework FastAPI. Esta elección nos permite construir APIs rápidas y de alto rendimiento con una sintaxis limpia y sencilla.

- **Python:** Un lenguaje versátil y poderoso, conocido por su legibilidad y simplicidad.
- **FastAPI:** Un moderno framework de alto rendimiento para construir APIs en Python, optimizado para obtener el mejor rendimiento gracias a su uso intensivo de async y await.

### Frontend: Angular

![Angular](https://img.shields.io/badge/Angular-12.0.0%2B-red?style=for-the-badge&logo=angular)

Para el frontend, utilizamos Angular, un framework de desarrollo web conocido por su capacidad de construir aplicaciones de una sola página (SPA) con una experiencia de usuario fluida y responsiva.

- **Angular:** Proporciona una sólida arquitectura basada en componentes y un ecosistema robusto para la gestión del estado y el enrutamiento de la aplicación.

### Base de Datos: PostgreSQL

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.0%2B-blue?style=for-the-badge&logo=postgresql)

PostgreSQL es la base de datos relacional elegida para este proyecto. Es conocida por su estabilidad, escalabilidad y capacidad de manejar grandes volúmenes de datos con eficiencia.

- **PostgreSQL:** Ofrece soporte para operaciones complejas y garantiza la integridad de los datos con características avanzadas como transacciones ACID y extensibilidad.

### Seguridad: JWT (JSON Web Tokens)

![JWT](https://img.shields.io/badge/JWT-JSON%20Web%20Tokens-orange?style=for-the-badge&logo=json-web-tokens)

La seguridad es una prioridad en el Proyecto Humble. Utilizamos JSON Web Tokens (JWT) para la autenticación y autorización, asegurando que las comunicaciones y el acceso a los recursos estén protegidos.

- **JWT:** Proporciona una forma compacta y segura de transmitir información entre partes, utilizada comúnmente para la autenticación basada en tokens en APIs web.

## Integración y Despliegue

![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-yellow?style=for-the-badge&logo=github-actions)

El despliegue y la integración continua son facilitados con GitHub Actions, asegurando que el código se construya, pruebe y despliegue de manera consistente y eficiente.

- **GitHub Actions:** Herramientas de CI/CD para automatizar el flujo de trabajo de desarrollo y despliegue, desde las pruebas hasta la entrega.


---

Para más información y preguntas sobre la configuración o el uso del backend del Proyecto Humble, no dudes en abrir un "issue" en este repositorio.

## Enlaces
[Repositorio del FrontEnd](https://github.com/Areshkew/humble-project-ui)
