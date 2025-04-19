"""
Model Context Protocol (MCP) streaming completions endpoint implementation.
Exposes POST /completion/complete/stream for SSE streaming of compliance results.
"""
from fastapi import APIRouter, Request
from fastapi.responses import EventSourceResponse
from ..core.compliance_checker import run_compliance_checks
from .mcp_utils import mcp_error_response, METHOD_NOT_FOUND, INVALID_PARAMS
from ..mcp_auth import mcp_auth_dependency
from fastapi import Depends
import asyncio

router = APIRouter()

@router.post("/completion/complete/stream")
async def completion_complete_stream(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    method = req_json.get("method")
    params = req_json.get("params", {})
    ref = params.get("ref", {})
    argument = params.get("argument", {})

    if method != "completion/complete" or ref.get("type") != "ref/prompt" or ref.get("name") != "code_review":
        return mcp_error_response(jsonrpc_id, METHOD_NOT_FOUND, "Unsupported method or prompt reference")
    code = argument.get("value", "")
    if not code:
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, "Missing code in argument.value")

    async def event_generator():
        results = run_compliance_checks(code)
        total = 0
        for category, items in results.items():
            if isinstance(items, list):
                for item in items:
                    total += 1
                    yield {"event": "completion", "data": f"{category}: {item}"}
                    await asyncio.sleep(0.05)
            elif isinstance(items, dict):
                for subcat, subitems in items.items():
                    for item in subitems:
                        total += 1
                        yield {"event": "completion", "data": f"{category}.{subcat}: {item}"}
                        await asyncio.sleep(0.05)
        yield {"event": "done", "data": str(total)}
    return EventSourceResponse(event_generator())
