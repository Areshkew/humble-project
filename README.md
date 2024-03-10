# Instrucciones
1. Revisa el archivo ".env", asegurate de que los datos de conexión a la base de datos sean correctos.
  En este archivo se encuentran las variables de entorno que se usaran para la conexión a la base de datos.
  Modifica los datos según tus necesidades, obligaciones o requerimientos.

2. Instala los requerimientos en tu entorno de python con el comando:
  ```bash
  pip install -r requirements.txt
  ```
3. Ejecuta el archivo "main.py" con el comando:
  ```bash
    python main.py
  ```

---

# Programas Necesarios o Dependencias
- Para la base de datos se usará PostgreSQL, por lo que se debe tener instalado en el sistema. 
  Si no se tiene instalado, se puede descargar desde su [página oficial](https://www.postgresql.org/download/).

- Al instalar PostgreSQL debes crear una base de datos con el mismo nombre en las variables de entorno en "DB_NAME", puesto que el backend
  se tratará de conectar a esta DB en especifico.

- Para el manejo del jwt, deberás crear una key RSA pública y privada desde aqui:
  [Generador de llaves RSA](https://cryptotools.net/rsagen) 
  y guardarlas en la carpeta "keys" con los nombres "private_key.pem" y "public_key.pem" respectivamente.

---

# Registro De Cambios

Todos los cambios serán documentados en este archivo.

## [Sin lanzar]


## [0.0.1] - 2024-03

### Arreglado
### Añadido
  #### Desarrollo: 
    - Utilidad de encriptacion de contraseñas 
    - Utilidad de desencriptacion de contraseñas
    - Conexión a la base de datos.
    - Mapeo de la estructura de la base de datos (repositories), para su uso a través del ORM.
    - Clase del usuario (models), usada para la verificación de datos en los futuros endpoints.
    - Controlador del usuario (usercontroller), se usará para la creación de endpoints.
    - Servicio del usuario (userservice), se usará para crear las operaciones que se podran realizar a través del controlador.
    - Creación de usuario root al iniciar el servidor. 
    - Creación de las preferencias de usuario.
  
  #### Caracteristicas:
    - Inicio y registro de cuentas.
    - Manejo de expiración de sesión.
    - Manejo de verificación de token.

### Removido
### Cambiado

