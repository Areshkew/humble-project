from fastapi import APIRouter

class UserController:
    def __init__(self):
        self.route = APIRouter()
        self.route.add_api_route("/", self.get_user, methods=["GET"])

    async def get_user(self):
        return {"user": "Hola"}

    