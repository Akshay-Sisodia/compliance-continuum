"""
Model Context Protocol (MCP) Resources endpoints implementation.
Exposes POST /resources/list and /resources/read for listing and reading files/resources.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import os
from .mcp_utils import mcp_error_response, INVALID_PARAMS
from ..mcp_auth import mcp_auth_dependency

router = APIRouter()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

@router.post("/resources/list")
async def resources_list(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    params = req_json.get("params", {})
    root_uri = params.get("rootUri")
    # Only support our project root for now
    if not root_uri or not root_uri.startswith("file://"):
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Missing or invalid rootUri")
    path = root_uri[7:].strip()
    if not os.path.isdir(path):
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Not a directory")
    entries = []
    all_entries = os.listdir(path)
    total = len(all_entries)
    limit = params.get("limit")
    offset = params.get("offset", 0)
    try:
        limit = int(limit) if limit is not None else None
        offset = int(offset) if offset is not None else 0
    except Exception:
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "limit and offset must be integers")
    paged_entries = all_entries[offset:offset+limit] if limit is not None else all_entries[offset:]
    for entry in paged_entries:
        entry_path = os.path.join(path, entry)
        entries.append({
            "uri": f"file://{entry_path.replace(os.sep, '/')}\n",
            "name": entry,
            "type": "directory" if os.path.isdir(entry_path) else "file"
        })
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": {"resources": entries, "total": total}
    })

@router.post("/resources/read")
async def resources_read(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    params = req_json.get("params", {})
    uri = params.get("uri")
    if not uri or not uri.startswith("file://"):
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Missing or invalid uri")
    path = uri[7:].strip()
    if not os.path.isfile(path):
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Not a file")
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": {"content": content}
    })
