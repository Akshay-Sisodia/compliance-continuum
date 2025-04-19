"""
JWT Authentication dependency for MCP endpoints.
Enable by setting MCP_AUTH_ENABLED=1 and MCP_JWT_SECRET in environment.
"""
import os
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from .api.mcp_utils import mcp_error_response

MCP_AUTH_ENABLED = os.getenv("MCP_AUTH_ENABLED", "0") == "1"
MCP_JWT_SECRET = os.getenv("MCP_JWT_SECRET", "supersecret")

def mcp_auth_dependency(request: Request):
    if not MCP_AUTH_ENABLED:
        return
    auth: HTTPAuthorizationCredentials = HTTPBearer(auto_error=False)(request)
    if not auth or not auth.credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        jwt.decode(auth.credentials, MCP_JWT_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
