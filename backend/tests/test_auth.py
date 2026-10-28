import pytest


def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "Password123!",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_email(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "Password123!",
            "full_name": "Dupe User"
        }
    )
    response = client.post(
        "/api/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "DifferentPassword123!",
            "full_name": "Dupe User 2"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_register_invalid_payload(client):
    # Short password (< 6 chars)
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalid@example.com",
            "password": "123"
        }
    )
    assert response.status_code == 422


def test_login_success_and_read_me(client):
    # Register first
    client.post(
        "/api/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "SecretPassword123!",
            "full_name": "Login User"
        }
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "SecretPassword123!"
        }
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["role"] == "user"
    assert token_data["email"] == "loginuser@example.com"

    token = token_data["access_token"]

    # Call /api/auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "loginuser@example.com"
    assert me_data["full_name"] == "Login User"


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401


def test_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
