from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()
VALID_PASSWORD = os.getenv("APP_PASSWORD", "futuropres47")

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
def login(data: LoginRequest):
    if data.password == VALID_PASSWORD:
        return {"status": "success", "message": "Acceso concedido", "token": "session_futuropres47_valid"}
    raise HTTPException(status_code=401, detail="Contraseña incorrecta")
