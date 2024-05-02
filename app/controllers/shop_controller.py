from app.services.shop_service import ShopService
from app.utils.class_utils import Injectable, inject
from app.utils.db_utils import get_db_session
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.models.shop_model import Shop, ShopDNIDelete, ShopUpdate

@inject(ShopService)
class ShopController(Injectable):
    def __init__(self):
        self.route = APIRouter(prefix='/shop')
        self.route.add_api_route("/get", self.get_shops, methods=["GET"])
        self.route.add_api_route("/create", self.create_shop, methods=["POST"])
        self.route.add_api_route("/delete", self.delete_shop, methods=["POST"])
        self.route.add_api_route("/edit/{shop_id}", self.edit_shop, methods=["POST"])
        self.route.add_api_route("/{shop_id}", self.shop_information, methods=["GET"])


    async def get_shops(self, request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario admin.")
        
        shops = await self.shopservice.get_shops(db)
        
        if not shops:
            raise HTTPException(status_code=403, detail="No se encontraron tiendas registradas")
        
        return shops


    async def create_shop(self, shop: Shop, request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario admin.")
        
        data = shop.model_dump()

        await self.shopservice.create_shop(data, db)

        return {"detail": "Se registró la tienda correctamente."}


    async def delete_shop(self, shop_ids: ShopDNIDelete, request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario admin.")
        
        shop_ids = shop_ids.model_dump()

        await ShopService().delete_shops(shop_ids["ids"], db)

        return {"sucess": True, "message": "Tiendas eliminadas exitosamente"}
        

    async def edit_shop(self, shop_id: int, shop_data: ShopUpdate, request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario admin.")
        
        data = shop_data.model_dump()
        
        data = {key: value for key, value in data.items() if value is not None} #Filtrar datos que no sean default

        await self.shopservice.update_shop(data, shop_id, db)
        return {"detail": "Se actualizo la tienda correctamente.", "success": True}
        

    async def shop_information(self, shop_id: int, request: Request, db: Session = Depends(get_db_session)):
        if request.state.payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Este recurso solo puede ser accedido por el usuario admin.")
        
        shop = await self.shopservice.get_shop_by_id(shop_id, db)
        
        if not shop:
            raise HTTPException(status_code=404, detail="Tienda no encontrada")

        return shop