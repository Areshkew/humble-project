from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.user_model import User, UserLogin
from app.services.user_service import UserService
from app.utils.auth import create_token
from app.utils.db_utils import get_db_session, verify_password

class UserController:
    def __init__(self):
        self.route = APIRouter(prefix='/user')
        self.route.add_api_route("/login", self.login, methods=["POST"])
        self.route.add_api_route("/signup", self.signup, methods=["POST"])
        self.service = UserService()

    async def login(self, user: UserLogin, db: Session = Depends(get_db_session)):
        data = user.model_dump()
        user_db = await self.service.get_user_dni_role(db, data["correo_electronico"])

        if user_db and verify_password(data["clave"], user_db["clave"]):
            token = create_token({
                "sub": user_db["DNI"],
                "role": user_db["rol"]
            })
            return {"detail": "Se inició sesión correctamente.", "token": token}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El email o contraseña no son válidos.")
            
    async def signup(self, user: User, db: Session = Depends(get_db_session)):
        data = user.model_dump()

        user_db = await self.service.account_exists(db, data["usuario"], data["correo_electronico"], data["DNI"])

        if not user_db:
            await self.service.create_account(db, data)
            
            token = create_token({
                "sub": data["DNI"],
                "role": "cliente"
            })
            return  {"detail": "Se registró la cuenta correctamente.", "token": token}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El usuario ya existe.")
