import pytest
from unittest.mock import Mock
from sqlalchemy import select
from tests.integration.conftest import TestingSessionLocal
from src.database.models import User
from src.conf.config import settings
from jose import jwt

user_data = {
    "user_name": "Niko",
    "user_email": "niko.man@gmail.com",
    "password": "123456789",
}


def generate_confirmation_token(email: str) -> str:
    return jwt.encode(
        {"sub": email},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


@pytest.mark.asyncio
async def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = await client.post("/api/auth/register", json=user_data)
    data = response.json()
    
    assert response.status_code == 201, response.text
    assert data["user_name"] == user_data["user_name"]
    assert data["user_email"] == user_data["user_email"]
    assert "hashed_password" not in data
    assert "avatar" in data


@pytest.mark.asyncio
async def test_signup_repeat(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = await client.post("/api/auth/register", json=user_data)
    data = response.json()

    assert response.status_code == 409, response.text
    assert data["detail"] == "User with such email already exists"


@pytest.mark.asyncio
async def test_signup_conflict_username(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = await client.post(
        "/api/auth/register",
        json={
            "user_name": user_data.get("user_name"),
            "user_email": "wrong.email@example.com",
            "password": "123456789",
        },
    )
    data = response.json()
    
    assert response.status_code == 409
    assert data["detail"] == "User with this name already exists"


@pytest.mark.asyncio
async def test_not_confirmed_login(client):
    response = await client.post(
        "api/auth/login",
        data={
            "username": user_data.get("user_name"),
            "password": user_data.get("password"),
        },
    )
    data = response.json()

    assert response.status_code == 401, response.text
    assert data["detail"] == "Email address not confirmed"


@pytest.mark.asyncio
async def test_confirm_email_success(client):
    token = generate_confirmation_token(user_data["user_email"])
    
    response = await client.get(f"/api/auth/confirmed_email/{token}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert data["message"] == "Email confirmed"
    
    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).where(User.user_email == user_data["user_email"]))
        user = user.scalar_one_or_none()
        assert user.confirmed is True


@pytest.mark.asyncio
async def test_confirm_email_already_confirmed(client):
    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).where(User.user_email == user_data["user_email"]))
        user = user.scalar_one_or_none()
        assert user is not None
        user.confirmed = True
        await session.commit()
    
    token = generate_confirmation_token(user_data["user_email"])
    
    response = await client.get(f"/api/auth/confirmed_email/{token}")
    data = response.json()

    assert response.status_code == 200, response.text
    assert data["message"] == "Your email has already been confirmed."
    

@pytest.mark.asyncio
async def test_confirm_email_invalid_email(client):
    token = generate_confirmation_token("wrong.email@example.com")
    
    response = await client.get(f"/api/auth/confirmed_email/{token}")
    data = response.json()

    assert response.status_code == 400, response.text
    assert data["detail"] == "Verification error"
    

@pytest.mark.asyncio
async def test_confirm_email_invalid_token(client):
    broken_token = "this.is.not.a.valid.jwt"
    
    response = await client.get(f"/api/auth/confirmed_email/{broken_token}")
    data = response.json()

    assert response.status_code == 422, response.text
    assert data["detail"] == "Invalid email verification token"


@pytest.mark.asyncio
async def test_request_send_if_not_confirmed(client, monkeypatch):
    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).where(User.user_email == user_data["user_email"]))
        user = user.scalar_one_or_none()
        assert user is not None
        user.confirmed = False
        await session.commit()

    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = await client.post("/api/auth/request_email", json={"user_email": user_data["user_email"]})
    data = response.json()

    assert response.status_code == 200, response.text
    assert data["message"] == "Check your email for confirmation."
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
async def test_request_already_confirmed(client, monkeypatch):
    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).where(User.user_email == user_data["user_email"]))
        user = user.scalar_one_or_none()
        assert user is not None
        user.confirmed = True
        await session.commit()

    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = await client.post("/api/auth/request_email", json={"user_email": user_data["user_email"]})
    data = response.json()

    assert response.status_code == 200, response.text
    assert data["message"] == "Your email has already been confirmed."
    mock_send_email.assert_not_called()


@pytest.mark.asyncio
async def test_request_email_user_not_found(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = await client.post("/api/auth/request_email", json={"user_email": "wrong.email@example.com"})
    data = response.json()

    assert response.status_code == 200, response.text
    assert data["message"] == "Check your email for confirmation."
    mock_send_email.assert_not_called()


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.user_name == user_data.get("user_name")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = await client.post(
        "api/auth/login", 
        data={
            "username": user_data.get("user_name"), 
            "password": user_data.get("password")
        },
    )
    data = response.json()

    assert response.status_code == 200, response.text
    assert "access_token" in data
    assert "token_type" in data



@pytest.mark.asyncio
async def test_wrong_password_login(client):
    response = await client.post(
        "api/auth/login", 
        data={
            "username": "wrrong_user_name", 
            "password": user_data.get("password")
        },
    )
    data = response.json()

    assert response.status_code == 401, response.text
    assert data["detail"] == "Incorrect login or password"


@pytest.mark.asyncio
async def test_wrong_username_login(client):
    response = await client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data

