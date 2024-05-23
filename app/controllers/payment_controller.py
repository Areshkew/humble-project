from app.models.payment_model import Card
from app.services.payment_service import PaymentService
from app.utils.db_utils import get_db_session
from app.utils.class_utils import Injectable, inject
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

@inject(PaymentService)
class PaymentController(Injectable):
    def __init__(self):
        self.route = APIRouter(prefix='/payment')
        self.route.add_api_route("/create-card", self.create_card, methods=["POST"])
        self.route.add_api_route("/delete-card/{card_num}", self.delete_card, methods=["POST"])
        self.route.add_api_route("/card/{card_num}", self.get_card, methods=["GET"])
        self.route.add_api_route("/cards", self.get_cards, methods=["GET"])
        self.route.add_api_route("/wallet", self.get_wallet, methods=["GET"])
        self.route.add_api_route("/add-balance", self.add_balance, methods=["POST"])



    async def create_card(self, request: Request, card: Card, db: Session = Depends(get_db_session)):
        card_dict = card.model_dump()

        card_exists = await self.paymentservice.card_exists(db, card_dict["num_tarjeta"])
        if card_exists:
            raise HTTPException(status_code=400, detail="El número de tarjeta ya existe")
        
        user_id = request.state.payload["sub"]
        card_dict["id_usuario"] = user_id

        await self.paymentservice.create_card(db, card_dict)
        return { "Success": True }


    async def delete_card(self, card_num: str, db: Session = Depends(get_db_session)):
        card_exists = await self.paymentservice.card_exists(db, card_num)
        if not card_exists:
            raise HTTPException(status_code=400, detail="El número de tarjeta no existe")
        
        await self.paymentservice.delete_card(db, card_num)
        return { "Success": True }


    async def get_card(self, card_num: str, db: Session = Depends(get_db_session)):
        card = await self.paymentservice.get_card(db, card_num)
        if not card:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
        return card
    

    async def get_cards(self, request: Request, db: Session = Depends(get_db_session)):
        user_id = request.state.payload["sub"]
        cards = await self.paymentservice.get_cards(db, user_id)
        if not cards:
            raise HTTPException(status_code=404, detail="Usuario sin tarjetas")
        return cards


    async def get_wallet(self, request: Request, db: Session = Depends(get_db_session)):
        user_id = request.state.payload["sub"]
        wallet = await self.paymentservice.get_wallet(db, user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Saldo de usuario no encontrado")
        return wallet
    
    async def add_balance(self, request: Request, data: dict, db: Session = Depends(get_db_session)):
        user_id = request.state.payload["sub"]
        saldo = data["saldo"]
        
        success = await self.paymentservice.add_balance(db, user_id, saldo)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo añadir el saldo")

        return { "Success": True }
