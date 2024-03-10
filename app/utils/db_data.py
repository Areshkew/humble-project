from app.repositories.genre_dao import GeneroDAO
from app.repositories.user_dao import UsuarioDAO
from app.repositories.userrole_dao import UsuarioRolDAO
from app.utils.db_utils import hash_password
import os

# Datos de los generos:
generos = [
    GeneroDAO(genero="Arte y Diseño"),
    GeneroDAO(genero="Autoayuda y Desarrollo Personal"),
    GeneroDAO(genero="Biografía/Autobiografía"),
    GeneroDAO(genero="Ciencia"),
    GeneroDAO(genero="Ciencia Ficción"),
    GeneroDAO(genero="Ciencia y Naturaleza"),
    GeneroDAO(genero="Crítica y Teoría Literaria"),
    GeneroDAO(genero="Deporte y Aventura"),
    GeneroDAO(genero="Educativo y Didáctico"),
    GeneroDAO(genero="Ensayo"),
    GeneroDAO(genero="Especializado"),
    GeneroDAO(genero="Estilo de Vida"),
    GeneroDAO(genero="Ficción General"),
    GeneroDAO(genero="Filosofía y Espiritualidad"),
    GeneroDAO(genero="Histórica"),
    GeneroDAO(genero="Infantil/Juvenil"),
    GeneroDAO(genero="Lingüística"),
    GeneroDAO(genero="Lingüística y Estudios de Lengua"),
    GeneroDAO(genero="Negocios y Economía"),
    GeneroDAO(genero="Novela Gráfica y Cómic"),
    GeneroDAO(genero="Salud y Bienestar"),
    GeneroDAO(genero="Sociedad y Cultura"),
    GeneroDAO(genero="Técnico y Científico"),
    GeneroDAO(genero="Thriller Legal"),
    GeneroDAO(genero="Viajes y Geografía")
]

# Datos de los roles:
roles = [
    UsuarioRolDAO(nombre="root"),
    UsuarioRolDAO(nombre="admin"),
    UsuarioRolDAO(nombre="cliente")
]

# Datos del usuario Root
root_data = {
    "DNI": "R000000",
    "correo_electronico": os.getenv("ROOT_EMAIL"),
    "usuario": os.getenv("ROOT_USER"),
    "clave": hash_password( os.getenv("ROOT_PASSWORD") ),
    "rol": 1
}