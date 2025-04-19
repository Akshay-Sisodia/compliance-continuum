"""
ModelContextProtocol (MCP) compatible endpoint for compliance checking.
Exposes POST /v1/compliance_check to accept code and return compliance results.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from ..core.compliance_checker import run_compliance_checks

router = APIRouter()

class MCPComplianceRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to check.")
    user_id: Optional[str] = Field(None, description="User ID (optional)")
    resource_id: Optional[str] = Field(None, description="Resource ID (optional)")

class MCPComplianceResponse(BaseModel):
    violations: dict

@router.post("/v1/compliance_check", response_model=MCPComplianceResponse)
def mcp_compliance_check(req: MCPComplianceRequest):
    results = run_compliance_checks(
        req.code,
        user_id=req.user_id,
        resource_id=req.resource_id
    )
    return {"violations": results}
