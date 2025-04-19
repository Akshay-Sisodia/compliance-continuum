"""
Model Context Protocol (MCP) Tools endpoint implementation.
Exposes POST /tools/list and /tools/call for listing and invoking tools.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ..core.compliance_checker import run_compliance_checks
from .mcp_utils import mcp_error_response, INVALID_PARAMS, METHOD_NOT_FOUND
from ..mcp_auth import mcp_auth_dependency
from fastapi import Depends

router = APIRouter()

@router.post("/tools/list")
async def tools_list(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    tools = [
        {
            "name": "run_compliance_check",
            "description": "Run compliance checks on provided code and return violations.",
            "params": [
                {"name": "code", "type": "string", "description": "Source code to check."}
            ],
            "returns": {"type": "array", "description": "List of detected violations."}
        }
    ]
    params = req_json.get("params", {})
    limit = params.get("limit")
    offset = params.get("offset", 0)
    try:
        limit = int(limit) if limit is not None else None
        offset = int(offset) if offset is not None else 0
    except Exception:
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "limit and offset must be integers")
    paged_tools = tools[offset:offset+limit] if limit is not None else tools[offset:]
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": {"tools": paged_tools, "total": len(tools)}
    })

@router.post("/tools/call")
async def tools_call(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    params = req_json.get("params", {})
    tool = params.get("tool")
    arguments = params.get("arguments", {})
    if tool != "run_compliance_check":
        return mcp_error_response(jsonrpc_id, METHOD_NOT_FOUND, "Tool not found")
    code = arguments.get("code", "")
    if not code:
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Missing code argument")
    results = run_compliance_checks(code)
    # Flatten all violations into a list of strings
    values = []
    for category, items in results.items():
        if isinstance(items, list):
            values.extend([f"{category}: {item}" for item in items])
        elif isinstance(items, dict):
            for subcat, subitems in items.items():
                values.extend([f"{category}.{subcat}: {item}" for item in subitems])
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": {"values": values}
    })
