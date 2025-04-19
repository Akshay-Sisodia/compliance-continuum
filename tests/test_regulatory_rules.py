import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_supabase
from app.models.regulatory_rule import RegulatoryRule
from sqlalchemy.orm import Session

import pytest

def test_dynamic_regulatory_rule_enforcement(client, auth_headers):
    # Add a new rule via API (admin only)
    rule_data = {
        "name": "No TODO allowed",
        "description": "Code must not contain TODO comments.",
        "pattern": r"TODO",
        "enabled": True
    }
    resp = client.post("/regulatory/rules", json=rule_data, headers=auth_headers)
    assert resp.status_code == 200
    rule_id = resp.json()["id"]
    # Submit code that violates the rule (authenticated)
    code = """
    def foo():
        # TODO: fix this
        pass
    """
    resp = client.post(
        "/compliance/check",
        json={
            "code": code,
            "user_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9",
            "resource_id": "8c586f51-d2bc-42a7-9e80-d2561604a6b9"
        },
        headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    # Check the regulatory_rules_violations field for the rule hit
    violations = data.get("regulatory_rules_violations", [])
    assert any(v.get("rule_id") == rule_id for v in violations), "Regulatory rule violation not detected in compliance check results"
    # Clean up: delete the rule
    client.delete(f"/regulatory/rules/{rule_id}", headers=auth_headers)
