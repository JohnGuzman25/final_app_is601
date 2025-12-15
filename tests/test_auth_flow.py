from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_page_loads():
    r = client.get("/auth/register")
    assert r.status_code == 200

def test_login_page_loads():
    r = client.get("/auth/login")
    assert r.status_code == 200
