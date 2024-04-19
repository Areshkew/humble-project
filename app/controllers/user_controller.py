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

        if not user_db["exists"]:
            await self.userservice.create_account(db, data)
            
            token = create_token({
                "sub": data["DNI"],
                "role": "cliente"
            })
            return  {"detail": "Se registró la cuenta correctamente.", "role": "cliente", "token": token}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Ya existe una cuenta con {' '.join(user_db['fields'].keys() )}, verifica los campos seleccionados.")


    async def passwordrecover(self, user: UserRecovery, db: Session = Depends(get_db_session)):
        data = user.model_dump()
        user_db = await self.userservice.account_exists(db, None, data["correo_electronico"], None)

        if user_db["exists"]:
            codigo = await self.userservice.generate_recovery_code()
            await self.userservice.store_code(db, data["correo_electronico"], codigo) 
            self.emailservice.send_email(data["correo_electronico"], "Codigo de recuperacion-Libhub", codigo)
            return {"detail": "Se envio el correo con exito.", "Success": "True"}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El correo electrónico no se encuentra en el sistema.") 
    

    async def codeverification(self, user: UserCode, db: Session = Depends(get_db_session)):
        data = user.model_dump()
        success = await self.userservice.verify_code(db, data["correo_electronico"], data["codigo"])

        if success:
            return {"detail": "El codigo ingresado se valido con el servidor.", "Success": True}
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="El codigo es invalido")
            

    async def newpassword(self, user: UserNewPassword, db: Session = Depends(get_db_session)):
        data = user.model_dump()

        if data["clave"] != data["claveRepetida"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Las contraseñas ingresadas no coinciden.")

        success = await self.userservice.update_password(db, data["correo_electronico"], data["clave"])

        if success:
            return {"detail": "La contraseña se cambio con exito.", "Success": True}
    

    async def getuserdata(self, user_fields: List[str], request: Request, db: Session = Depends(get_db_session)):
        data = request.state.payload["sub"]

        if "role" not in request.state.payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo acceder a la petición.")
    
        if request.state.payload["role"] == "guest":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo acceder a la petición.")

        user_data = await self.userservice.get_user_data(db, data, user_fields)

        return user_data


    async def editaccount(self, user: UserUpdate, request: Request, db: Session = Depends(get_db_session)):
        data = user.model_dump()
        dni = request.state.payload["sub"]
        
        data = {key: value for key, value in data.items() if value is not None} #Filtrar datos que no sean default
        
        if request.state.payload["role"] == "root" and any(field != "clave" for field in data.keys()):
            raise HTTPException(status_code=403, detail="El usuario root solo puede editar su contraseña.")
        
        if request.state.payload["role"] not in ["admin", "cliente","root"]:
            raise HTTPException(status_code=403, detail="No se pudo acceder a la petición.")
        
        if any(field == "clave" for field in data.keys()) and any(field == "clave_actual" for field in data.keys()):
            old_pass = await self.userservice.get_user_pass(db, dni)
            
            if verify_password(data["clave_actual"], old_pass):
                await self.userservice.update_account(db, data, dni)            
                return {"detail": "Se actualizo la cuenta correctamente.", "success": True}
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="La contraseña actual no coincide con la de la base de datos.")            
        else:
            await self.userservice.update_account(db, data, dni)
            return {"detail": "Se actualizo la cuenta correctamente.", "success": True}