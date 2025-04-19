from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..db import get_supabase
import uuid

router = APIRouter()
supabase = get_supabase()

class AlertIn(BaseModel):
    type: str = Field(...)
    message: str = Field(...)
    severity: str = Field("info")

class AlertOut(AlertIn):
    id: uuid.UUID
    created_at: str
    read: bool

from app.api.auth import get_current_user, get_current_admin_user
from fastapi import Depends

@router.post("/alerts", response_model=AlertOut)
def create_alert(alert: AlertIn, current_user: dict = Depends(get_current_admin_user)):
    data = alert.dict()
    data["read"] = False
    res = supabase.table("alerts").insert(data).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    a = res.data[0]
    return AlertOut(
        id=a["id"],
        type=a["type"],
        message=a["message"],
        severity=a["severity"],
        created_at=a["created_at"],
        read=a["read"]
    )

@router.get("/alerts", response_model=list[AlertOut])
def get_alerts(current_user: dict = Depends(get_current_user)):
    res = supabase.table("alerts").select("*").order("created_at", desc=True).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return [
        AlertOut(
            id=a["id"],
            type=a["type"],
            message=a["message"],
            severity=a["severity"],
            created_at=a["created_at"],
            read=a["read"]
        ) for a in res.data
    ]

@router.put("/alerts/{alert_id}", response_model=AlertOut)
def mark_alert_read(alert_id: uuid.UUID, current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("alerts").update({"read": True}).eq("id", str(alert_id)).execute()
    if res.error or not res.data:
        raise HTTPException(status_code=404, detail="Alert not found or update failed")
    a = res.data[0]
    return AlertOut(
        id=a["id"],
        type=a["type"],
        message=a["message"],
        severity=a["severity"],
        created_at=a["created_at"],
        read=a["read"]
    )

@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: uuid.UUID, current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("alerts").delete().eq("id", str(alert_id)).execute()
    if res.error:
        raise HTTPException(status_code=404, detail="Alert not found or delete failed")
    return {"detail": "Alert deleted"}

