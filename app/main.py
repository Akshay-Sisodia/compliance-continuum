"""
Main entrypoint for Compliance Continuum MCP Server.
Initializes FastAPI app, logging, and API routers.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .api import compliance
from .api import regulatory
from .api import alert
from .api import report
from .api import users
from .api import auth
from .api import compliance_protocol
from .api import mcp_completion
from .api import mcp_roots
from .api import mcp_resources
from .api import mcp_prompts
from .api import mcp_tools
from .api import mcp_logging
from .api import mcp_completion_stream
from .api import mcp_docs
from .logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger("main")

app = FastAPI(
    title="Compliance Continuum — MCP Server",
    description="""
A secure, production-grade compliance system for code review and regulatory enforcement.\n\n
**Features:**
- JWT Authentication and RBAC
- Automated compliance checks for PII, vulnerabilities, GDPR, discrimination
- Dynamic regulatory rule enforcement
- Audit logging and reporting
- Supabase integration
    """,
    version="1.0.0",
    contact={
        "name": "Compliance Team",
        "email": "support@yourdomain.com",
        "url": "https://yourdomain.com/compliance"
    }
)

# Register routers
app.include_router(compliance.router)
app.include_router(regulatory.router)
app.include_router(alert.router)
app.include_router(report.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(compliance_protocol.router)
app.include_router(mcp_completion.router)
app.include_router(mcp_roots.router)
app.include_router(mcp_resources.router)
app.include_router(mcp_prompts.router)
app.include_router(mcp_tools.router)
app.include_router(mcp_logging.router)
app.include_router(mcp_completion_stream.router)
app.include_router(mcp_docs.router)

@app.on_event("startup")
def on_startup():
    logger.info("Server startup: Compliance Continuum MCP Server")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

app.include_router(compliance.router)
app.include_router(regulatory.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Compliance Continuum MCP Server is running."}
