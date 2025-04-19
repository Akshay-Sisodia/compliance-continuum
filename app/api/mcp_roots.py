"""
Model Context Protocol (MCP) Roots endpoint implementation.
Exposes POST /roots/list for listing available roots (workspaces/projects).
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import os
from .mcp_utils import mcp_error_response, INVALID_PARAMS
from ..mcp_auth import mcp_auth_dependency

router = APIRouter()

# For demonstration, we'll use the project root as the only root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

@router.post("/roots/list")
async def roots_list(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    root_uri = req_json.get("rootUri")
    if not root_uri or not root_uri.startswith("file://"):
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Missing or invalid rootUri")
    path = root_uri[7:].strip()
    if not os.path.isdir(path):
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Not a directory")
    result = {
        "roots": [
            {
                "uri": f"file://{PROJECT_ROOT.replace(os.sep, '/')}\n",
                "name": "Compliance Continuum",
                "type": "workspace"
            }
        ]
    }
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": result
    })
