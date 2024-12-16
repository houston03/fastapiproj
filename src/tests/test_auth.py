import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.database import Base, get_db
from app.database.models import User as UserModel
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("TEST_DATABASE_URL is not set in environment variables")

engine = create_async_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(scope="module")
async def db():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        await db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.mark.asyncio
async def test_create_user(client, db):
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "phone_number": "1234567890"
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["phone_number"] == user_data["phone_number"]

@pytest.mark.asyncio
async def test_login_for_access_token(client, db):
    # Создаем пользователя для теста
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "phone_number": "1234567890"
    }
    await client.post("/users/", json=user_data)

    # Логинимся
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == user_data["username"]
    assert data["user"]["email"] == user_data["email"]
