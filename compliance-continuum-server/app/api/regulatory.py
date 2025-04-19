from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..db import get_supabase
import uuid

router = APIRouter()
supabase = get_supabase()

class RegulatoryRuleIn(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    pattern: str = Field(...)
    enabled: bool = True

class RegulatoryRuleOut(RegulatoryRuleIn):
    id: uuid.UUID
    created_at: str
    updated_at: str

from app.api.auth import get_current_user, get_current_admin_user
from fastapi import Depends

@router.post("/regulatory/rules", response_model=RegulatoryRuleOut)
def create_rule(rule: RegulatoryRuleIn, current_user: dict = Depends(get_current_admin_user)):
    data = rule.dict()
    res = supabase.table("regulatory_rules").insert(data).execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=400, detail=res.error.message)
    r = res.data[0]
    return RegulatoryRuleOut(
        id=r["id"],
        name=r["name"],
        description=r["description"],
        pattern=r["pattern"],
        enabled=r["enabled"],
        created_at=r["created_at"],
        updated_at=r["updated_at"]
    )

@router.get("/regulatory/rules", response_model=list[RegulatoryRuleOut])
def get_rules(current_user: dict = Depends(get_current_user)):
    res = supabase.table("regulatory_rules").select("*").execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=400, detail=res.error.message)
    return [
        RegulatoryRuleOut(
            id=r["id"],
            name=r["name"],
            description=r["description"],
            pattern=r["pattern"],
            enabled=r["enabled"],
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        ) for r in res.data
    ]

@router.put("/regulatory/rules/{rule_id}", response_model=RegulatoryRuleOut)
def update_rule(rule_id: uuid.UUID, rule: RegulatoryRuleIn, current_user: dict = Depends(get_current_admin_user)):
    update_data = rule.dict()
    res = supabase.table("regulatory_rules").update(update_data).eq("id", str(rule_id)).execute()
    if getattr(res, "error", None) or not getattr(res, "data", None):
        raise HTTPException(status_code=404, detail="Rule not found or update failed")
    r = res.data[0]
    return RegulatoryRuleOut(
        id=r["id"],
        name=r["name"],
        description=r["description"],
        pattern=r["pattern"],
        enabled=r["enabled"],
        created_at=r["created_at"],
        updated_at=r["updated_at"]
    )

@router.delete("/regulatory/rules/{rule_id}")
def delete_rule(rule_id: uuid.UUID, current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("regulatory_rules").delete().eq("id", str(rule_id)).execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=404, detail="Rule not found or delete failed")
    return {"detail": "Rule deleted"}

