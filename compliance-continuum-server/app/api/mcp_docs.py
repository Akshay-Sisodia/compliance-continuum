"""
Custom endpoint for Model Context Protocol (MCP) documentation and usage examples.
Exposes GET /mcp-docs with protocol summary and integration instructions.
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

MCP_DOCS = """
<h2>Model Context Protocol (MCP) API Documentation</h2>
<p>This server implements the <a href='https://modelcontextprotocol.io'>Model Context Protocol</a> for code compliance checking and related tools.</p>
<h3>Authentication</h3>
<ul>
<li>Set <b>MCP_AUTH_ENABLED=1</b> and <b>MCP_JWT_SECRET</b> in your environment to enable JWT authentication.</li>
<li>Send <b>Authorization: Bearer &lt;token&gt;</b> header with all MCP requests.</li>
</ul>
<h3>Endpoints</h3>
<ul>
<li><b>/roots/list</b>: List workspace roots (POST, JSON-RPC 2.0)</li>
<li><b>/resources/list</b>: List files/resources in a root (POST, JSON-RPC 2.0, supports pagination)</li>
<li><b>/resources/read</b>: Read a file/resource (POST, JSON-RPC 2.0)</li>
<li><b>/prompts/list</b>: List available prompts (POST, JSON-RPC 2.0, supports pagination)</li>
<li><b>/tools/list</b>: List available tools (POST, JSON-RPC 2.0, supports pagination)</li>
<li><b>/tools/call</b>: Call a tool (POST, JSON-RPC 2.0)</li>
<li><b>/completion/complete</b>: Run compliance checks (POST, JSON-RPC 2.0)</li>
<li><b>/completion/complete/stream</b>: Stream compliance results (POST, JSON-RPC 2.0, SSE)</li>
<li><b>/logging/setLevel</b>: Set server log level (POST, JSON-RPC 2.0)</li>
<li><b>/logging/logMessage</b>: Log a message (POST, JSON-RPC 2.0)</li>
</ul>
<h3>Usage Example</h3>
<pre>{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "completion/complete",
  "params": {
    "ref": { "type": "ref/prompt", "name": "code_review" },
    "argument": { "name": "language", "value": "def foo(): pass" }
  }
}
</pre>
<h3>See also:</h3>
<ul>
<li><a href='/docs'>OpenAPI (Swagger) Docs</a></li>
<li><a href='https://modelcontextprotocol.io'>MCP Protocol Reference</a></li>
</ul>
"""

@router.get("/mcp-docs", response_class=HTMLResponse)
def mcp_docs():
    return MCP_DOCS
