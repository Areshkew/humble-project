from pydantic import BaseModel, Field, validator
from datetime import  datetime

class Card(BaseModel):
    tipo: bool = Field(...)  # 0: Debito, 1: Credito
    num_tarjeta: str = Field(..., min_length=16, max_length=16)
    fec_vencimiento: datetime = Field(...)
    cvv: str = Field(..., min_length=3, max_length=3)

    @validator('fec_vencimiento', pre=True)
    def parse_fecha_publicacion(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                raise ValueError("Formato de fecha Inválido")
        return value
    
