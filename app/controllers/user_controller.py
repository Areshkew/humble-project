from fastapi import APIRouter
from app.services.user_service import UserService

class UserController:
    def __init__(self, service: UserService = UserService):
        self.route = APIRouter()
        self.route.add_api_route("/", self.get_user, methods=["GET"])

    async def get_user(self):
        return {"user": "Hola"}

    