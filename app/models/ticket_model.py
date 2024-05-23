from pydantic import BaseModel, Field, validator
from datetime import  datetime

class TicketCreate(BaseModel):
    id_usuario: str = Field(..., min_length=7, max_length=10)
    asunto: str = Field(..., min_length=1, max_length=1024)
    
class TicketRespond(BaseModel):
    id_ticket: int = Field(...)
    id_usuario: str = Field(..., min_length=7, max_length=10)
    mensaje: str = Field(..., min_length=1, max_length=1024)
    fecha: datetime = Field(...)

    @validator('fecha', pre=True)
    def parse_fecha_publicacion(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                raise ValueError("Formato de fecha Inválido")
        return value