# Compliance Continuum Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A secure, production-grade compliance system for code review and regulatory enforcement. Features robust authentication, role-based access control, dynamic regulatory rule enforcement, detailed audit logging, and comprehensive testing.

**GitHub Repository:** [https://github.com/Akshay-Sisodia/compliance-continuum](https://github.com/Akshay-Sisodia/compliance-continuum)

## Features
- **JWT Authentication**: Secure login with stateless JWT tokens.
- **Role-Based Access Control**: Admin and user roles restrict access to sensitive endpoints.
- **Compliance Checks**: Automated detection of PII, vulnerabilities, GDPR violations, and discrimination in code.
- **Dynamic Regulatory Rules**: Add, update, and enforce custom compliance rules via API.
- **Audit Logging**: All compliance checks and rule changes are logged for traceability.
- **Supabase Integration**: Modern, scalable backend for users, rules, and logs.
- **Production-Ready Security**: Password hashing, strict RBAC, and secure configuration.
- **Comprehensive Tests**: End-to-end and unit tests for all major features.

## Quickstart

### 1. Clone & Install
```bash
git clone https://github.com/Akshay-Sisodia/compliance-continuum.git
cd compliance-continuum/compliance-continuum-server
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your Supabase and secret keys.

### 3. Run the Server
```bash
uvicorn app.main:app --reload
```

### 4. Run Tests
```bash
pytest --disable-warnings -v
```

## API Overview
- **POST /auth/token**: Obtain JWT token (login)
- **POST /compliance/check**: Run compliance checks on code
- **POST /regulatory/rules**: Create a new regulatory rule (admin)
- **GET /regulatory/rules**: List all rules
- **PUT /regulatory/rules/{id}**: Update a rule (admin)
- **DELETE /regulatory/rules/{id}**: Delete a rule (admin)
- **POST /audit/logs**: Query audit logs

See the FastAPI docs at `/docs` when the server is running for details and schemas.

---

## Model Context Protocol (MCP) Usage

This server implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) for code compliance checking, tool calls, and resource management via JSON-RPC 2.0 endpoints.

### MCP Endpoints
- **/completion/complete**: Run compliance checks (POST, JSON-RPC 2.0)
- **/completion/complete/stream**: Stream compliance results (POST, JSON-RPC 2.0, SSE)
- **/tools/list**: List available tools (POST, JSON-RPC 2.0)
- **/tools/call**: Call a tool (POST, JSON-RPC 2.0)
- **/resources/list**: List files/resources (POST, JSON-RPC 2.0)
- **/resources/read**: Read a file/resource (POST, JSON-RPC 2.0)
- **/prompts/list**: List available prompts (POST, JSON-RPC 2.0)
- **/roots/list**: List available roots/workspaces (POST, JSON-RPC 2.0)
- **/logging/setLevel**: Set server log level (POST, JSON-RPC 2.0)
- **/logging/logMessage**: Log a message (POST, JSON-RPC 2.0)

### Authentication
MCP endpoints require JWT authentication. Obtain a token via `/auth/token` and include it as a Bearer token in the `Authorization` header.

### Example: Compliance Completion Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "completion/complete",
  "params": {
    "ref": { "type": "ref/prompt", "name": "code_review" },
    "argument": { "name": "language", "value": "def foo(): pass" }
  }
}
```

### Example: Tool Call (Compliance Check)
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "tool": "run_compliance_check",
    "arguments": { "code": "def foo(): pass" }
  }
}
```

### More MCP Docs
- Visit `/mcp-docs` on the running server for a full protocol summary and usage examples.
- See the [Model Context Protocol Reference](https://modelcontextprotocol.io) for integration details.

---

## Repository Structure
- `compliance-continuum-server/` — Main server code and documentation
- `compliance_dashboard.py` — Dashboard utility script
- `PRD.md`, `COMPLIANCE.md`, `GDPR_COMPLIANCE.md`, etc. — Documentation

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Environment Variables
See `.env.example` for all required variables:
- `SUPABASE_URL`, `SUPABASE_KEY`: Supabase project credentials
- `SECRET_KEY`: JWT signing key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT expiration
- `REDIS_URL`: For Celery/background jobs (optional)

## Security Notes
- All secrets must be kept in `.env` (never commit real secrets)
- Only admins can manage regulatory rules
- Passwords are always hashed (never stored in plain text)

## Deployment
You can deploy with any ASGI server (e.g., Uvicorn, Gunicorn) and a managed Postgres/Supabase backend.