"""
Compliance API endpoints for code checks, audit logs, and regulatory rule enforcement.
Includes request/response models and endpoint logic.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..db import get_supabase
from ..core.compliance_checker import run_compliance_checks
from ..core.ethical_enforcer import (
    detect_pii, detect_security_vulnerabilities,
    detect_discriminatory_patterns, detect_gdpr_violations, ml_pattern_detection
)
from ..core.audit import add_audit_log, get_audit_logs
from ..models.audit_log import ActionType, ComplianceStatus
import uuid

router = APIRouter()
supabase = get_supabase()

class ComplianceRequest(BaseModel):
    """
    Request model for submitting code to compliance checks.
    """
    code: str = Field(..., min_length=1, description="Source code to check.")
    context: str = None
    user_id: uuid.UUID = Field(..., description="User UUID performing the check.")
    resource_id: uuid.UUID = Field(..., description="Resource UUID (e.g., file or commit).")

class ComplianceResponse(BaseModel):
    """
    Response model for compliance checks, including standard checks and regulatory rule violations.
    """
    pii: list[str]
    vulnerabilities: list[str]
    gdpr: list[str]
    discrimination: list[str]
    ethical_enforcer: dict
    regulatory_rules_violations: list[dict] = []

@router.post("/compliance/check", response_model=ComplianceResponse)
def compliance_check(req: ComplianceRequest):
    """
    Run all compliance checks (PII, vulnerabilities, GDPR, discrimination, regulatory rules, external API, ML analysis) on submitted code.
    Logs the check in the audit log.
    Returns detailed results and ethical flags.
    """
    checks = run_compliance_checks(
        req.code,
        user_id=str(req.user_id),
        resource_id=str(req.resource_id)
    )
    ethical = {
        "pii": checks.get("pii", []),
        "vulnerabilities": checks.get("vulnerabilities", []),
        "discrimination": checks.get("discrimination", []),
        "gdpr": checks.get("gdpr", []),
        "ml_flag": checks.get("ml_analysis", {}).get("risk_score") if "ml_analysis" in checks else None
    }
    status = ComplianceStatus.COMPLIANT if not any(
        v for k, v in checks.items() if k not in ["ml_analysis", "ethical_enforcer"]
    ) else ComplianceStatus.NON_COMPLIANT
    from ..core.audit import add_audit_log
    add_audit_log(
        user_id=req.user_id,
        action_type=ActionType.ACCESS,
        resource_id=req.resource_id,
        changes=checks,
        compliance_status=status
    )
    # Return all advanced module results in the response
    return ComplianceResponse(
        pii=checks.get("pii", []),
        vulnerabilities=checks.get("vulnerabilities", []),
        gdpr=checks.get("gdpr", []),
        discrimination=checks.get("discrimination", []),
        regulatory_rules_violations=checks.get("regulatory_rules_violations", []),
        ethical_enforcer=ethical
    )

class AuditLogQuery(BaseModel):
    """
    Request model for querying audit logs by user, resource, or limit.
    """
    user_id: uuid.UUID = None
    resource_id: uuid.UUID = None
    limit: int = 100

@router.post("/audit/logs")
def query_audit_logs(query: AuditLogQuery):
    """
    Query audit logs filtered by user, resource, or limit.
    Returns a list of audit log entries.
    """
    from ..core.audit import get_audit_logs
    logs = get_audit_logs(user_id=query.user_id, resource_id=query.resource_id, limit=query.limit)
    return [
        {
            "id": str(log["id"]),
            "timestamp": log["timestamp"],
            "user_id": str(log["user_id"]),
            "action_type": log["action_type"],
            "resource_id": str(log["resource_id"]),
            "changes": log["changes"],
            "compliance_status": log["compliance_status"],
        }
        for log in logs
    ]

