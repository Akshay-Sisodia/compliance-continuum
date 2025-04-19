import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def auth_headers(client):
    # Use pre-created admin user from Supabase
    username = "apitestuser"
    password = "testpass123"
    resp = client.post("/auth/token", data={"username": username, "password": password})
    print(f"Auth token status: {resp.status_code}, response: {resp.text}")
    assert resp.status_code == 200, f"Failed to obtain token: {resp.text}"
    data = resp.json()
    assert "access_token" in data, f"No access_token in response: {data}"
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}
