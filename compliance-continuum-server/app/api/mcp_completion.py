"""
Model Context Protocol (MCP) completion endpoint implementation for code compliance.
Exposes POST /completion/complete accepting JSON-RPC 2.0 requests per MCP spec.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ..core.compliance_checker import run_compliance_checks
from .mcp_utils import mcp_error_response, METHOD_NOT_FOUND, INVALID_PARAMS
from ..mcp_auth import mcp_auth_dependency
from fastapi import Depends

router = APIRouter()

@router.post("/completion/complete")
async def completion_complete(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    method = req_json.get("method")
    params = req_json.get("params", {})
    ref = params.get("ref", {})
    argument = params.get("argument", {})

    # Only support code_review prompt for now
    if method != "completion/complete" or ref.get("type") != "ref/prompt" or ref.get("name") != "code_review":
        return mcp_error_response(jsonrpc_id, METHOD_NOT_FOUND, "Unsupported method or prompt reference")

    code = argument.get("value", "")
    if not code:
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Missing code in argument.value")

    # Run compliance checks
    results = run_compliance_checks(code)

    # Flatten all violations into a single list of strings
    values = []
    for category, items in results.items():
        if isinstance(items, list):
            values.extend([f"{category}: {item}" for item in items])
        elif isinstance(items, dict):
            for subcat, subitems in items.items():
                values.extend([f"{category}.{subcat}: {item}" for item in subitems])

    response = {
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": {
            "completion": {
                "values": values[:100],
                "total": len(values),
                "hasMore": len(values) > 100
            }
        }
    }
    return JSONResponse(content=response)
