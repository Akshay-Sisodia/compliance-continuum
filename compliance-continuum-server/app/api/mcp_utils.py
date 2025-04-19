"""
Utility functions for MCP-compliant error responses (JSON-RPC 2.0).
"""
from fastapi.responses import JSONResponse

def mcp_error_response(jsonrpc_id, code, message, status_code=400):
    return JSONResponse(
        {
            "jsonrpc": "2.0",
            "id": jsonrpc_id,
            "error": {"code": code, "message": message}
        },
        status_code=status_code
    )

# Standard JSON-RPC error codes
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
