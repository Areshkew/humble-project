from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.user_model import *
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.utils.auth import create_token
from app.utils.class_utils import Injectable, inject
from app.utils.db_utils import get_db_session, verify_password

@inject(UserService)
@inject(EmailService)
class UserController(Injectable):
    def __init__(self):
        self.route = APIRouter(prefix='/user')
        self.route.add_api_route("/login", self.login, methods=["POST"])
        self.route.add_api_route("/signup", self.signup, methods=["POST"])

    async def login(self, user: UserLogin, db: Session = Depends(get_db_session)):
        data = user.model_dump()
        user_db = await self.userservice.get_user_dni_role(db, data["correo_electronico"])
        password_verification = await verify_password(data["clave"], user_db["clave"])

        if user_db and await password_verification:
            token = create_token({
                "sub": user_db["DNI"],
                "role": user_db["rol"]
            })
            return {"detail": "Se inició sesión correctamente.", "role": user_db["rol"], "token": token}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El email o contraseña no son válidos.")
            
    async def signup(self, user: User, db: Session = Depends(get_db_session)):
        data = user.model_dump()

        user_db = await self.userservice.account_exists(db, data["usuario"], data["correo_electronico"], data["DNI"])

        if not user_db:
            await self.userservice.create_account(db, data)
            
            token = create_token({
                "sub": data["DNI"],
                "role": "cliente"
            })
            return  {"detail": "Se registró la cuenta correctamente.", "role": "cliente", "token": token}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El usuario ya existe.")

    async def passwordrecover(self, user: UserRecovery, db: Session = Depends(get_db_session)):
        data = user.model_dump()
        user_db = await self.userservice.account_exists(db, None, data["correo_electronico"], None)

        if user_db:
            codigo = await self.userservice.generate_recovery_code()
            await self.userservice.store_code(db, data["correo_electronico"], codigo) 
            self.emailservice.send_email(data["correo_electronico"], codigo)
            return {"detail": "Se envio el correo con exito."}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El email no existe o no es valido") 
    
    async def codeverification(self, user: UserCode, db: Session = Depends(get_db_session)):
        pass

    async def newpassword(self, user: UserNewPassword, db: Session = Depends(get_db_session)):
        pass
