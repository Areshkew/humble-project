from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.models.user_model import *
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.utils.auth import create_token
from app.utils.class_utils import Injectable, inject
from app.utils.db_utils import get_db_session, verify_password

@inject(UserService, EmailService)
class UserController(Injectable):
    def __init__(self):
        self.route = APIRouter(prefix='/user')
        self.route.add_api_route("/login", self.login, methods=["POST"])
        self.route.add_api_route("/signup", self.signup, methods=["POST"])
        self.route.add_api_route("/passwordrecover", self.passwordrecover, methods=["POST"])
        self.route.add_api_route("/codeverification", self.codeverification, methods=["POST"])
        self.route.add_api_route("/newpassword", self.newpassword, methods=["POST"])
        self.route.add_api_route("/getuserdata", self.getuserdata, methods=["POST"])
        self.route.add_api_route("/editaccount", self.editaccount, methods=["POST"])


    async def login(self, user: UserLogin, db: Session = Depends(get_db_session)):
        data = user.model_dump()

        user_db = await self.userservice.get_user_dni_role(db, data["correo_electronico"])

        if user_db:
            password_verification = verify_password(data["clave"], user_db["clave"])
            if password_verification:
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
            self.emailservice.send_email(data["correo_electronico"], "Codigo de recuperacion-Libhub", codigo)
            return {"detail": "Se envio el correo con exito.", "Success": "True"}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El email no existe o no es valido") 
    

    async def codeverification(self, user: UserCode, db: Session = Depends(get_db_session)):
        data = user.model_dump()
        success = await self.userservice.verify_code(db, data["correo_electronico"], data["codigo"])

        if success:
            return {"detail": "El codigo es correcto", "Success": "True"}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El codigo es invalido")
            

    async def newpassword(self, user: UserNewPassword, db: Session = Depends(get_db_session)):
        data = user.model_dump()

        success = await self.userservice.update_password(db, data["correo_electronico"], data["clave"], data["claveRepetida"])

        if success:
            return {"detail": "Contraseña cambiada con exito", "Success": "True"}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Las dos contraseñas no coinciden")
    

    async def getuserdata(self, user_fields: List[str], request: Request, db: Session = Depends(get_db_session)):
        data = request.state.payload["sub"]

        if "role" not in request.state.payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Rol de usuario no encontrado")
    
        if request.state.payload["role"] == "guest":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Rol visitante")

        user_data = await self.userservice.get_user_data(db, data, user_fields)

        return user_data


    async def editaccount(self, user: UserUpdate, request: Request, db: Session = Depends(get_db_session)):
        data = user.model_dump()
        dni = request.state.payload["sub"]

        data = {key: value for key, value in data.items() if value is not None} #Filtrar datos que no sean default


        if request.state.payload["role"] == "root" and any(field != "clave" for field in data.keys()):
            raise HTTPException(status_code=403, detail="El root solo puede editar su contraseña")
        
        if request.state.payload["role"] not in ["admin", "cliente","root"]:
            raise HTTPException(status_code=403, detail="No tienes permiso para editar esta cuenta")
        
        user_db = await self.userservice.account_exists(db, data.get("usuario"), data.get("correo_electronico"), data.get("DNI"))


        if not user_db:
            await self.userservice.update_account(db, data, dni)
            if data.get("DNI") is not None:
                token = create_token({
                    "sub": data["DNI"],
                    "role": "cliente"
                    })
            else:
                token = create_token({
                    "sub": dni,
                    "role": "cliente"
                    })
            return  {"detail": "Se actualizo la cuenta correctamente.", "role": "cliente", "token": token}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Datos ya existentes")
                            