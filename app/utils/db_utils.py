from db.connection import SessionLocal
from db.base_class import Base
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from typing import AsyncGenerator
from app.repositories.models import *

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
        Obtiene una sesión asincrona hacía la base de datos.

        Cada que se use un endpoint, se creará una nueva sesión y se cerrará al finalizar la petición.
        Esto se debe a que "yield" es un generador, por lo que se ejecutará hasta que se termine de usar.
        Un generador es un iterador que solo se puede recorrer una vez, por lo que al finalizar la petición, la sesión se cerrará.
    """
    async with SessionLocal() as session:
        yield session

async def create_tables(engine: AsyncEngine) -> None:
    """
        Crea las tablas en la base de datos.

        Nota: Este método se ejecutará al inicializar el servidor, pero solo se crearan las tablas si no existen.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def db_operation(db_session_key: str = 'db'):
    """
        Decorador para operaciones en la base de datos.
        
        Automatiza "commit" que se debe hacer al finalizar una operación en la base de datos.
        y "refresh" para obtener los cambios realizados en la base de datos.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            db: AsyncSession = kwargs.get(db_session_key, None)
            if db is None:
                raise ValueError(f"AsyncSession not found '{db_session_key}'")
            result = await func(*args, **kwargs)
            await db.commit()
            if result is not None:
                await db.refresh(result)
            return result
        return wrapper
    return decorator
