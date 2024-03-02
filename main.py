from app.services.user_service import UserService
from app.utils.db_utils import create_tables, get_db_session
from contextlib import asynccontextmanager
from app.controllers.user_controller import UserController
from db.connection import engine
from fastapi import FastAPI
import uvicorn

class ServerBootstrap:
    """
        ServerBootstrap es responsable de inicializar el servidor.
        Se encarga de inicializar la aplicación de FastAPI y de inicializar los controladores.

        Los controladores son clases que se encargan de manejar las peticiones HTTP.
    """
    def __init__(self, app: FastAPI):
        self.app = app
        self.user_controller = UserController()
        self.app.include_router(self.user_controller.route) 

    def run(self):
        uvicorn.run(self.app, host="localhost", port=8000)

    @asynccontextmanager
    @staticmethod
    async def start_up_events(app: FastAPI):
        await create_tables(engine)

        async for session in get_db_session():
            try:
                user_service = UserService()
                await user_service.create_root_user(session)
            finally:
                await session.close()

        yield
    
def main():
    app = FastAPI(lifespan=ServerBootstrap.start_up_events)

    ServerBootstrap(app).run()

if __name__ == "__main__":
    main()