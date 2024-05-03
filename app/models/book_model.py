from datetime import  datetime
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Annotated, Optional, List

class BookISSNDelete(BaseModel):
    issn_list: Annotated[List[Annotated[str, Field(min_length=7, max_length=15)]],
                            Field(default=None, min_items=1, max_items=10)]
    
class Book(BaseModel):
    ISSN: str = Field(..., min_length=13, max_length=13, pattern=r'^\d{13}$')
    autor: str = Field(..., min_length=1, max_length=100)
    descuento: Optional[float] = Field(None, gt=0)
    editorial: str = Field(..., min_length=1, max_length=100)
    estado: bool = Field(...)
    fecha_publicacion: datetime = Field(...)
    genero: int = Field(...)
    idioma: str = Field(..., min_length=1, max_length=50)
    num_paginas: int = Field(..., gt=0)
    precio: float = Field(..., gt=0)
    resenia: str = Field(..., min_length=1, max_length=500)
    titulo: str = Field(..., min_length=1, max_length=200)
    portada: str = Field(...)

    @validator('fecha_publicacion', pre=True)
    def parse_fecha_publicacion(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                raise ValueError("Formato de fecha Inválido")
        return value
