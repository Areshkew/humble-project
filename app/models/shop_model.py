from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional, List

class Shop(BaseModel):
    ubicacion: Annotated[str, Field(..., min_length=1, max_length=64)]
    nombre: Annotated[str, Field(..., min_length=1, max_length=64)]
    num_contacto: Annotated[str, Field(..., min_length=10, max_length=10)]
    correo: Annotated[EmailStr, Field(..., min_length=1, max_length=64)]
    hora_apertura: Annotated[str, Field(..., min_length=1, max_length=8)] #Formato XX:XX
    hora_cierre: Annotated[str, Field(..., min_length=1, max_length=8)] #Formato XX:XX

class ShopDNIDelete(BaseModel):
    ids: Annotated[List[int], Field(default=None, min_items=1, max_items=3)]

class ShopUpdate(BaseModel):
    ubicacion: Optional[str] = Field(default=None, min_length=1, max_length=64)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=64)
    num_contacto: Optional[str] = Field(default=None, min_length=10, max_length=10)
    correo: Optional[EmailStr] = Field(default=None, min_length=1, max_length=64)
    hora_apertura: Optional[str] = Field(default=None, min_length=1, max_length=8)
    hora_cierre: Optional[str] = Field(default=None, min_length=1, max_length=8)
