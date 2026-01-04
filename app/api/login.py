from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import ADMIN_USERNAME, ADMIN_PASSWORD
from app.core.jwt_utils import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    if req.username != ADMIN_USERNAME or req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
    "sub": req.username,
    "role": "admin"
})

    return {"access_token": token, "token_type": "bearer"}
