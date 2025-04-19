from fastapi import APIRouter, Response
from ..db import get_supabase
import csv
import io

router = APIRouter()
supabase = get_supabase()

@router.get("/report/audit_logs/csv")
def export_audit_logs_csv():
    res = supabase.table("audit_logs").select("*").order("timestamp", desc=True).execute()
    if res.error:
        return Response(content="Error exporting audit logs: " + res.error.message, media_type="text/plain", status_code=500)
    logs = res.data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "user_id", "action_type", "resource_id", "changes", "compliance_status", "timestamp"])
    for log in logs:
        writer.writerow([
            log["id"], log["user_id"], log["action_type"], log["resource_id"], log["changes"], log["compliance_status"], log["timestamp"]
        ])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/report/alerts/csv")
def export_alerts_csv():
    res = supabase.table("alerts").select("*").order("created_at", desc=True).execute()
    if res.error:
        return Response(content="Error exporting alerts: " + res.error.message, media_type="text/plain", status_code=500)
    alerts = res.data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "type", "message", "severity", "created_at", "read"])
    for a in alerts:
        writer.writerow([
            a["id"], a["type"], a["message"], a["severity"], a["created_at"], a["read"]
        ])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/report/regulatory_rules/csv")
def export_rules_csv():
    res = supabase.table("regulatory_rules").select("*").execute()
    if res.error:
        return Response(content="Error exporting rules: " + res.error.message, media_type="text/plain", status_code=500)
    rules = res.data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "description", "pattern", "enabled", "created_at", "updated_at"])
    for r in rules:
        writer.writerow([
            r["id"], r["name"], r["description"], r["pattern"], r["enabled"], r["created_at"], r["updated_at"]
        ])
    return Response(content=output.getvalue(), media_type="text/csv")

@router.get("/report/policies/csv")
def export_policies_csv():
    res = supabase.table("policies").select("*").execute()
    if res.error:
        return Response(content="Error exporting policies: " + res.error.message, media_type="text/plain", status_code=500)
    policies = res.data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "description", "content", "enabled", "created_at", "updated_at"])
    for p in policies:
        writer.writerow([
            p.id, p.name, p.description, p.content, p.enabled, p.created_at.isoformat(), p.updated_at.isoformat()
        ])
    return Response(content=output.getvalue(), media_type="text/csv")
