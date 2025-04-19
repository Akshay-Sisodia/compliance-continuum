import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Dummy UUIDs for testing
def dummy_uuid():
    return uuid.uuid4()

def test_compliance_check_compliant():
    req = {
        "code": "def foo():\n    return 42",
        "user_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9",
        "resource_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9"
    }
    resp = client.post("/compliance/check", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert all(len(v) == 0 for k, v in data.items() if k != "ethical_enforcer")
    assert data["ethical_enforcer"]["pii"] is False
    assert data["ethical_enforcer"]["vulnerabilities"] is False
    assert data["ethical_enforcer"]["discrimination"] is False
    assert data["ethical_enforcer"]["gdpr"] is False

def test_compliance_check_pii():
    req = {
        "code": "email = 'test@example.com'",
        "user_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9",
        "resource_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9"
    }
    resp = client.post("/compliance/check", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}" in data["pii"]
    assert data["ethical_enforcer"]["pii"] is True

def test_compliance_check_vulnerability():
    req = {
        "code": "eval('2+2')",
        "user_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9",
        "resource_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9"
    }
    resp = client.post("/compliance/check", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert any("eval" in pat for pat in data["vulnerabilities"])
    assert data["ethical_enforcer"]["vulnerabilities"] is True

def test_audit_log_query():
    req = {
        "code": "def foo(): return 1",
        "user_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9",
        "resource_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9"
    }
    client.post("/compliance/check", json=req)
    query = {"limit": 1}
    resp = client.post("/audit/logs", json=query)
    assert resp.status_code == 200
    logs = resp.json()
    assert isinstance(logs, list)
    assert len(logs) > 0
    assert "id" in logs[0]
    assert "timestamp" in logs[0]
    assert "user_id" in logs[0]
    assert "changes" in logs[0]
