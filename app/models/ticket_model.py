from pydantic import BaseModel, Field, validator
from datetime import  datetime

class TicketCreate(BaseModel):
    id_usuario: str = Field(..., min_length=7, max_length=10)
    asunto: str = Field(..., min_length=1, max_length=1024)
    
class TicketRespond(BaseModel):
    id_ticket: int = Field(...)
    id_usuario: str = Field(..., min_length=7, max_length=10)
    mensaje: str = Field(..., min_length=1, max_length=1024)