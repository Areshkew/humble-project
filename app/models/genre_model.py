from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

class Genre(BaseModel):
    id: Annotated[int, Field(...)]
    genero: Annotated[str, Field(..., min_length=1, max_length=32)]