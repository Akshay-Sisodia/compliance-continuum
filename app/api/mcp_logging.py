"""
Model Context Protocol (MCP) Logging endpoints implementation.
Exposes POST /logging/setLevel and /logging/logMessage for log level management and log notifications.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
from .mcp_utils import mcp_error_response, INVALID_PARAMS
from ..mcp_auth import mcp_auth_dependency
from fastapi import Depends

router = APIRouter()

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

current_log_level = logging.INFO

@router.post("/logging/setLevel")
async def set_log_level(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    params = req_json.get("params", {})
    level = params.get("level", "info").lower()
    if level not in LOG_LEVELS:
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, f"Invalid log level: {level}")
    global current_log_level
    current_log_level = LOG_LEVELS[level]
    logging.getLogger().setLevel(current_log_level)
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": {"level": level}
    })

@router.post("/logging/logMessage")
async def log_message(request: Request, _=Depends(mcp_auth_dependency)):
    req_json = await request.json()
    jsonrpc_id = req_json.get("id")
    params = req_json.get("params", {})
    level = params.get("level", "info").lower()
    message = params.get("message", "")
    if level not in LOG_LEVELS:
        return mcp_error_response(jsonrpc_id, INVALID_PARAMS, f"Invalid log level: {level}")
    logging.log(LOG_LEVELS[level], message)
    # Per MCP, this could also emit a notification, but for now just acknowledge
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": jsonrpc_id,
        "result": {"message": "logged", "level": level}
    })
