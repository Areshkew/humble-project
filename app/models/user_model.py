from app.models.genre_model import Genre
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional, List

class User(BaseModel):
    DNI: Annotated[str, Field(..., min_length=7, max_length=10)]
    nombre: Annotated[str, Field(..., min_length=1, max_length=32)]
    apellido: Annotated[str, Field(..., min_length=1, max_length=32)]
    fecha_nacimiento: Annotated[str, Field(..., min_length=1, max_length=32)]
    pais: Annotated[str, Field(..., min_length=1, max_length=32)]
    estado: Annotated[str, Field(..., min_length=1, max_length=32)]
    ciudad: Annotated[str, Field(..., min_length=1, max_length=32)]
    direccion_envio: Annotated[str, Field(..., min_length=1, max_length=64)]
    genero: Annotated[str, Field(..., min_length=1, max_length=16)]
    correo_electronico: Annotated[EmailStr, Field(...)]
    usuario: Annotated[str, Field(..., min_length=1, max_length=32)]
    clave: Annotated[str, Field(..., min_length=5, max_length=32)]
    suscrito_noticias: Annotated[bool, None]
    preferencias: Optional[List[Genre]] = None

class UserLogin(BaseModel):
    correo_electronico: Annotated[EmailStr, Field(...)]
    clave: Annotated[str, Field(..., min_length=5, max_length=32)]