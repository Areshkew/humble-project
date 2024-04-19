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
    suscrito_noticias: Optional[bool] = None
    preferencias: Optional[List[Genre]] = Field(default=None, min_items=1, max_items=3)

class UserLogin(BaseModel):
    correo_electronico: Annotated[EmailStr, Field(...)]
    clave: Annotated[str, Field(..., min_length=5, max_length=32)]

class UserRecovery(BaseModel):
    correo_electronico: Annotated[EmailStr, Field(...)]

class UserCode(BaseModel):
    correo_electronico: Annotated[EmailStr, Field(...)]
    codigo: Annotated[str, Field(..., length=8)]

class UserNewPassword(BaseModel):
    correo_electronico: Annotated[EmailStr, Field(...)]
    clave: Annotated[str, Field(..., min_length=5, max_length=32)]
    claveRepetida: Annotated[str, Field(..., min_length=5, max_length=32)]

class UserUpdate(BaseModel):
    DNI: Optional[str] = Field(default=None, min_length=7, max_length=10)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=32)
    apellido: Optional[str] = Field(default=None, min_length=1, max_length=32)
    fecha_nacimiento: Optional[str] = Field(default=None, min_length=1, max_length=32)
    pais: Optional[str] = Field(default=None, min_length=1, max_length=32)
    estado: Optional[str] = Field(default=None, min_length=1, max_length=32)
    ciudad: Optional[str] = Field(default=None, min_length=1, max_length=32)
    direccion_envio: Optional[str] = Field(default=None, min_length=1, max_length=64)
    genero: Optional[str] = Field(default=None, min_length=1, max_length=16)
    correo_electronico: Optional[EmailStr] = Field(default=None)
    usuario: Optional[str] = Field(default=None, min_length=1, max_length=32)
    clave: Optional[str] = Field(default=None, min_length=5, max_length=32)
    clave_actual: Optional[str] = Field(default=None, min_length=5, max_length=32)
    suscrito_noticias: Optional[bool] = Field(default=None)
    preferencias: Optional[List[Genre]] = Field(default=None, min_items=1, max_items=3)

class UserDNIDelete(BaseModel):
    dnis: Annotated[List[Annotated[str, Field(min_length=7, max_length=10)]],
                            Field(default=None, min_items=1, max_items=3)]
