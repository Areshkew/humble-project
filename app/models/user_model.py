from datetime import date
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional

class User(BaseModel):
    DNI: Annotated[str, Field(..., min_length=7, max_length=10)]
    nombre: Optional[str] = Field(default=None, max_length=32)
    apellido: Optional[str] = Field(default=None, max_length=32)
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = Field(default=None, max_length=32)
    direccion_envio: Optional[str] = Field(default=None, max_length=64)
    genero: Optional[str] = Field(default=None, max_length=16)
    correo_electronico: Annotated[EmailStr, Field(...)]
    usuario: Annotated[str, Field(..., min_length=1, max_length=32)]
    clave: Annotated[str, Field(..., min_length=1, max_length=128)]
    suscrito_noticias: Optional[bool] = None
    saldo: Optional[float] = None
    rol: Optional[str] = None