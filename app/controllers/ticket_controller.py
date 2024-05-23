from app.utils.db_utils import get_db_session
from app.utils.class_utils import Injectable, inject
from app.services.ticket_service import TicketService
from app.models.ticket_model import TicketCreate, TicketRespond
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

@inject(TicketService)
class TicketController(Injectable):
    def __init__(self):
        self.route = APIRouter(prefix='/ticket')
        self.route.add_api_route("/create", self.create_ticket, methods=["POST"])
        self.route.add_api_route("/respond", self.respond_to_ticket, methods=["POST"])
        self.route.add_api_route("/response/{ticket_id}", self.get_ticket_response, methods=["GET"])
        self.route.add_api_route("/delete/{ticket_id}", self.delete_ticket, methods=["POST"])


    async def create_ticket(self, data: TicketCreate, db: Session = Depends(get_db_session)):
        dict = data.model_dump()
        await self.ticketservice.create_ticket(db, dict)
        return {"detail": "Ticket creado con exito", "success": "True"}


    async def respond_to_ticket(self, data: TicketRespond, db: Session = Depends(get_db_session)):
        dict = data.model_dump()

        ticket_exists = await self.ticketservice.ticket_exist(db, data.id_ticket)
        if not ticket_exists:
            raise HTTPException(status_code=400, detail="El ticket no existe")

        await self.ticketservice.respond_to_ticket(db, dict)
        return {"success" : "True"}


    async def get_ticket_response(self, ticket_id: int, db: Session = Depends(get_db_session)):
        response = await self.ticketservice.get_ticket_response(db, ticket_id)

        if not response:
             raise HTTPException(status_code=404, detail="El ticket no tiene respuestas")
        
        return response


    async def delete_ticket(self, ticket_id: int, db: Session = Depends(get_db_session)):
        ticket_exists = await self.ticketservice.ticket_exist(db, ticket_id)

        if not ticket_exists:
            raise HTTPException(status_code=400, detail="El ticket no existe")

        await self.ticketservice.delete_ticket(db, ticket_id)
        return {"detail": "Ticked eliminado con exito", "success": "True"}
