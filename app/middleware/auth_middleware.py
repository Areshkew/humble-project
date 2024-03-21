from app.utils.auth import verify_token
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization_header = request.headers.get("Authorization")
        if authorization_header:
            try:
                scheme, token = authorization_header.split(" ")
                if scheme.lower() == "bearer":
                    payload = verify_token(token)
                    request.state.role = payload.get("role", "guest")
                else:
                    request.state.role = "guest"
            except (ValueError, HTTPException):
                request.state.role = "guest"
        else:
            request.state.role = "guest"
        
        response = await call_next(request)
        return response
