from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.models.user_model import *
from app.services.user_service import UserService
from app.services.book_service import BookService
from app.services.email_service import EmailService
from app.utils.auth import create_token
from app.utils.class_utils import Injectable, inject
from app.utils.db_utils import get_db_session, verify_password

@inject(UserService, EmailService, BookService)
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
        self.route.add_api_route("/saldo/{id}", self.get_saldo, methods=["GET"])
        self.route.add_api_route("/realizar-compra", self.realizar_compra, methods=["POST"])


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
            self.emailservice.send_email(
                            recipient=data["correo_electronico"],
                            subject="[Libhub] - Codigo de recuperacion de contraseña",
                            template_path='templates/password_recovery.html',
                            html=True,
                            template_data={'code': codigo, 'support_email': 'libhub.contact@gmail.com'}
                        )
            
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
        
        if request.state.payload["role"] == "root" and any( (field != "clave" and field != "clave_actual" and field != "confirmar-clave") for field in data.keys()):
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
        
    async def get_saldo(self, id: str, db: Session = Depends(get_db_session)):
        saldo = await self.userservice.saldo_user(id, db)
        
        if saldo:
            return saldo
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Este usuario no tiene saldo")  
        
    async def realizar_compra(self, request: CompraRequest, db: Session = Depends(get_db_session)):
        userId = request.userId
        booksForShop = request.booksForShop

        count_dict = {}

        for book in booksForShop:
            if book in count_dict:
                count_dict[book] += 1
            else:
                count_dict[book] = 1

        #Valida que haya unidades suficientes
        for key in count_dict.keys():
            if await self.bookservice.validar_cantidades(key[0], key[1], count_dict[key], db):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="No existen unidades suficientes") 
        
        if not booksForShop:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Los libros no han sido enviados")
        
        if not userId:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="El usuario no ha sido enviado")  
        
        #Valida que si tenga suficiente saldo
        saldo = 0
        for book in booksForShop:
            saldo += await self.bookservice.calcularSaldo(book[0], db)
        saldoUser = await self.userservice.saldo_user(userId, db)

        if saldoUser < saldo:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="No hay suficiente saldo")


        await self.userservice.generar_factura(userId, saldo, db)
        for book in booksForShop:
            idBookNuevo = await self.bookservice.realizar_compra(userId, book[0], book[1], db)
            await self.userservice.generar_factura_libro(idBookNuevo, userId, saldo, db)

        await self.userservice.borrarReservas(userId, db)

        return True