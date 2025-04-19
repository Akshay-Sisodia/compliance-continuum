from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..db import get_supabase
import uuid

router = APIRouter()
supabase = get_supabase()

class UserIn(BaseModel):
    username: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)
    is_admin: bool = False

class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: str

class PolicyIn(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    content: str = Field(...)
    enabled: bool = True

class PolicyOut(PolicyIn):
    id: uuid.UUID
    created_at: str
    updated_at: str

# User endpoints (existing)
@router.post("/admin/users", response_model=UserOut)
def create_user(user: UserIn):
    hashed = user.password + "_hashed"
    data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed,
        "is_admin": user.is_admin,
        "is_active": True  # default active
    }
    res = supabase.table("users").insert(data).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    u = res.data[0]
    return UserOut(
        id=u["id"],
        username=u["username"],
        email=u["email"],
        is_active=u["is_active"],
        is_admin=u["is_admin"],
        created_at=u["created_at"]
    )


@router.get("/admin/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        UserOut(
            id=u.id,
            username=u.username,
            email=u.email,
            is_active=u.is_active,
            is_admin=u.is_admin,
            created_at=u.created_at.isoformat()
        ) for u in users
    ]

@router.put("/admin/users/{user_id}", response_model=UserOut)
def update_user(user_id: uuid.UUID, user: UserIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.username = user.username
    u.email = user.email
    u.hashed_password = user.password + "_hashed"
    u.is_admin = user.is_admin
    db.commit()
    db.refresh(u)
    return UserOut(
        id=u.id,
        username=u.username,
        email=u.email,
        is_active=u.is_active,
        is_admin=u.is_admin,
        created_at=u.created_at.isoformat()
    )

@router.delete("/admin/users/{user_id}")
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(u)
    db.commit()
    return {"detail": "User deleted"}

# Policy endpoints (new)
@router.post("/admin/policies", response_model=PolicyOut)
def create_policy(policy: PolicyIn):
    data = policy.dict()
    res = supabase.table("policies").insert(data).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    p = res.data[0]
    return PolicyOut(
        id=p["id"],
        name=p["name"],
        description=p["description"],
        content=p["content"],
        enabled=p["enabled"],
        created_at=p["created_at"],
        updated_at=p["updated_at"]
    )


@router.get("/admin/policies", response_model=list[PolicyOut])
def list_policies():
    res = supabase.table("policies").select("*").execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return [
        PolicyOut(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            content=p["content"],
            enabled=p["enabled"],
            created_at=p["created_at"],
            updated_at=p["updated_at"]
        ) for p in res.data
    ]


@router.put("/admin/policies/{policy_id}", response_model=PolicyOut)
def update_policy(policy_id: uuid.UUID, policy: PolicyIn):
    update_data = policy.dict()
    res = supabase.table("policies").update(update_data).eq("id", str(policy_id)).execute()
    if res.error or not res.data:
        raise HTTPException(status_code=404, detail="Policy not found or update failed")
    p = res.data[0]
    return PolicyOut(
        id=p["id"],
        name=p["name"],
        description=p["description"],
        content=p["content"],
        enabled=p["enabled"],
        created_at=p["created_at"],
        updated_at=p["updated_at"]
    )


@router.delete("/admin/policies/{policy_id}")
def delete_policy(policy_id: uuid.UUID):
    res = supabase.table("policies").delete().eq("id", str(policy_id)).execute()
    if res.error:
        raise HTTPException(status_code=404, detail="Policy not found or delete failed")
    return {"detail": "Policy deleted"}


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.user import User
import uuid

router = APIRouter()

class UserIn(BaseModel):
    username: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)
    is_admin: bool = False

class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: str

@router.post("/admin/users", response_model=UserOut)
def create_user(user: UserIn, db: Session = Depends(get_db)):
    # Hash password (simple example, use passlib in prod)
    hashed = user.password + "_hashed"
    u = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed,
        is_admin=user.is_admin
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return UserOut(
        id=u.id,
        username=u.username,
        email=u.email,
        is_active=u.is_active,
        is_admin=u.is_admin,
        created_at=u.created_at.isoformat()
    )

@router.get("/admin/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        UserOut(
            id=u.id,
            username=u.username,
            email=u.email,
            is_active=u.is_active,
            is_admin=u.is_admin,
            created_at=u.created_at.isoformat()
        ) for u in users
    ]

@router.put("/admin/users/{user_id}", response_model=UserOut)
def update_user(user_id: uuid.UUID, user: UserIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.username = user.username
    u.email = user.email
    u.hashed_password = user.password + "_hashed"
    u.is_admin = user.is_admin
    db.commit()
    db.refresh(u)
    return UserOut(
        id=u.id,
        username=u.username,
        email=u.email,
        is_active=u.is_active,
        is_admin=u.is_admin,
        created_at=u.created_at.isoformat()
    )

@router.delete("/admin/users/{user_id}")
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(u)
    db.commit()
    return {"detail": "User deleted"}
