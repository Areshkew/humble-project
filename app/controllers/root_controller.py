from app.models.user_model import User, UserUpdate
from app.services.root_service import RootService
from app.services.user_service import UserService
from app.utils.auth import create_token
from app.utils.db_utils import get_db_session
from app.utils.class_utils import Injectable, inject
from app.models.user_model import UserDNIDelete
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

@inject(RootService, UserService)
class RootController(Injectable):
    def __init__(self):
        self.route = APIRouter(prefix='/root')
        self.route.add_api_route("/admins", self.get_admins, methods=["GET"])
        self.route.add_api_route("/create-admin", self.create_admin, methods=["POST"])
        self.route.add_api_route("/delete-admins", self.delete_admins, methods=["POST"])
        self.route.add_api_route("/edit-admin/{admin_id}", self.edit_admin, methods=["POST"])
        self.route.add_api_route("/admin/{admin_id}", self.get_admin, methods=["POST"])

    async def get_admins(self, request: Request, db: Session = Depends(get_db_session)):   
        if request.state.payload["role"] != "root":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario root.")

        admins = await self.rootservice.get_admins(db)

        if not admins:
            raise HTTPException(status_code=403, detail="No se encontraron administradores registrados.")
            
        return admins
    
    async def create_admin(self, user: User, request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "root":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario root.")

        data = user.model_dump()

        user_db = await self.userservice.account_exists(db, data["usuario"], data["correo_electronico"], data["DNI"])

        if not user_db["exists"]:
            await self.userservice.create_account(db, data, 2) # Role 2 admin
            
            return  {"detail": "Se registró la cuenta correctamente."}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Ya existe una cuenta con {' '.join(user_db['fields'].keys() )}, verifica los campos seleccionados.")
    
    async def delete_admins(self, request: Request, dni_list: UserDNIDelete, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "root":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario root.")

        dni_list = dni_list.model_dump()
        
        await self.rootservice.delete_admins(db, dni_list["dnis"])

        return {"success": True}
    
    async def edit_admin(self, admin_id: str,  user: UserUpdate, request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "root":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario root.")
        
        data = user.model_dump()
        dni = admin_id
        
        data = {key: value for key, value in data.items() if value is not None} #Filtrar datos que no sean default
    
        
        await self.userservice.update_account(db, data, dni)
        return {"detail": "Se actualizo la cuenta correctamente.", "success": True}

    async def get_admin(self, admin_id: str, user_fields: list[str], request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "root":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario root.")
        
        data = admin_id
        
        user_data = await self.userservice.get_user_data(db, data, user_fields)

        return user_data
