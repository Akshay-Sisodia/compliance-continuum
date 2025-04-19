"""
Model Context Protocol (MCP) Prompts endpoint implementation.
Exposes POST /prompts/list for listing available prompts.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .mcp_utils import mcp_error_response, INVALID_PARAMS
from ..mcp_auth import mcp_auth_dependency
from fastapi import Depends

router = APIRouter()

@router.post("/prompts/list")
async def prompts_list(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    # Only one prompt for now: code_review
    prompts = [
        {
            "name": "code_review",
            "description": "Analyze code for compliance, vulnerabilities, and risks.",
            "inputType": "code",
            "outputType": "violations"
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
    paged_prompts = prompts[offset:offset+limit] if limit is not None else prompts[offset:]
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": {"prompts": paged_prompts, "total": len(prompts)}
    })
