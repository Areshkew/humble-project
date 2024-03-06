from datetime import date
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional

class User(BaseModel):
    DNI: Annotated[str, Field(..., min_length=7, max_length=10)]
    nombre: Annotated[str, Field(default=None, max_length=32)]
    apellido: Annotated[str, Field(default=None, max_length=32)]
    fecha_nacimiento: Annotated[date, None]
    lugar_nacimiento: Annotated[str, Field(default=None, max_length=32)]
    direccion_envio: Annotated[str, Field(default=None, max_length=64)]
    genero: Annotated[str, Field(default=None, max_length=16)]  
    correo_electronico: Annotated[EmailStr, Field(...)]
    usuario: Annotated[str, Field(..., min_length=1, max_length=32)]
    clave: Annotated[str, Field(..., min_length=1, max_length=32)]
    suscrito_noticias: Annotated[bool, None]
    saldo: Annotated[float, None]
    # rol: Annotated[str, None]

class UserLogin(BaseModel):
    correo_electronico: Annotated[EmailStr, Field(...)]
    clave: Annotated[str, Field(..., min_length=1, max_length=32)]