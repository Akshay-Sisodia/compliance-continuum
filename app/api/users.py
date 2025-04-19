from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from ..db import get_supabase
import uuid

class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: str

router = APIRouter()
supabase = get_supabase()

from fastapi import Depends
from app.api.auth import get_password_hash, get_current_admin_user

@router.get("/users", response_model=list[UserOut])
def list_users(current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("users").select("*").execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=400, detail=res.error.message)
    return [
        UserOut(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            is_admin=u["is_admin"],
            is_active=u["is_active"],
            created_at=u["created_at"]
        ) for u in res.data
    ]

class UserCreate(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    is_admin: bool = False

@router.post("/users", response_model=UserOut)
def create_user(user: UserCreate, current_user: dict = Depends(get_current_admin_user)):
    # Enforce unique username/email
    existing = supabase.table("users").select("*").or_(f"username.eq.{user.username},email.eq.{user.email}").execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_password = get_password_hash(user.password)
    data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_admin": user.is_admin,
        "is_active": True
    }
    res = supabase.table("users").insert(data).execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=400, detail=res.error.message)
    u = res.data[0]
    return UserOut(
        id=u["id"],
        username=u["username"],
        email=u["email"],
        is_admin=u["is_admin"],
        is_active=u["is_active"],
        created_at=u["created_at"]
    )
