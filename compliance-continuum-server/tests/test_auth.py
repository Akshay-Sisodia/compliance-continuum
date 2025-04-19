import pytest

def test_admin_login_and_access(client):
    username = "apitestuser"
    password = "testpass123"
    email = "apitestuser@example.com"
    # Login
    resp = client.post("/auth/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    # Use token for authenticated endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["username"] == username
    assert me.json()["email"] == email
