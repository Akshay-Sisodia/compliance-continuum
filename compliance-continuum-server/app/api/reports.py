from fastapi import APIRouter, Query, Response, HTTPException
from typing import Optional
from app.db import get_supabase
import csv
import io

router = APIRouter()
supabase = get_supabase()

@router.get("/reports/health")
def get_health_report():
    return {"status": "ok", "message": "Reporting API is online."}

from app.api.auth import get_current_user, get_current_admin_user
from fastapi import Depends

@router.get("/reports/compliance_summary")
def compliance_summary(user_id: Optional[str] = None, resource_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    # Only allow users to view their own summaries unless admin
    if not current_user.get("is_admin", False):
        user_id = str(current_user["id"])
    query = supabase.table("audit_logs").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    if resource_id:
        query = query.eq("resource_id", resource_id)
    res = query.execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=500, detail=res.error.message)
    logs = res.data
    compliant = sum(1 for l in logs if l["compliance_status"] == "COMPLIANT")
    non_compliant = sum(1 for l in logs if l["compliance_status"] == "NON_COMPLIANT")
    return {
        "total_checks": len(logs),
        "compliant": compliant,
        "non_compliant": non_compliant,
        "compliance_rate": compliant / len(logs) if logs else 1.0
    }

@router.get("/reports/audit_logs")
def get_audit_logs(user_id: Optional[str] = None, resource_id: Optional[str] = None, limit: int = 100, current_user: dict = Depends(get_current_user)):
    # Only allow users to view their own logs unless admin
    if not current_user.get("is_admin", False):
        user_id = str(current_user["id"])
    query = supabase.table("audit_logs").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    if resource_id:
        query = query.eq("resource_id", resource_id)
    query = query.order("timestamp", desc=True).limit(limit)
    res = query.execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=500, detail=res.error.message)
    return res.data

@router.get("/reports/audit_logs/csv")
def export_audit_logs_csv(limit: int = 100, current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("audit_logs").select("*").order("timestamp", desc=True).limit(limit).execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=500, detail=res.error.message)
    logs = res.data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "user_id", "action_type", "resource_id", "changes", "compliance_status", "timestamp"])
    for log in logs:
        writer.writerow([
            log["id"], log["user_id"], log["action_type"], log["resource_id"], log["changes"], log["compliance_status"], log["timestamp"]
        ])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/reports/alerts")
def get_alerts(limit: int = 100, current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("alerts").select("*").order("created_at", desc=True).limit(limit).execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=500, detail=res.error.message)
    return res.data

@router.get("/reports/alerts/csv")
def export_alerts_csv(limit: int = 100, current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("alerts").select("*").order("created_at", desc=True).limit(limit).execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=500, detail=res.error.message)
    alerts = res.data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "type", "message", "severity", "created_at", "read"])
    for a in alerts:
        writer.writerow([
            a["id"], a["type"], a["message"], a["severity"], a["created_at"], a["read"]
        ])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/reports/regulatory_rules")
def get_regulatory_rules(current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("regulatory_rules").select("*").execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=500, detail=res.error.message)
    return res.data

@router.get("/reports/regulatory_rules/csv")
def export_rules_csv(current_user: dict = Depends(get_current_admin_user)):
    res = supabase.table("regulatory_rules").select("*").execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=500, detail=res.error.message)
    rules = res.data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "description", "pattern", "enabled", "created_at", "updated_at"])
    for r in rules:
        writer.writerow([
            r["id"], r["name"], r["description"], r["pattern"], r["enabled"], r["created_at"], r["updated_at"]
        ])
    return Response(content=output.getvalue(), media_type="text/csv")
