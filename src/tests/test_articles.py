import pytest
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.app.database.models import Base, User as UserModel, Article as ArticleModel
from src.app.schemas.user import UserCreate
from src.app.schemas.post import ArticleCreate
from sqlalchemy import select

DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost:5432/blogapp"

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db():
    async with async_session() as session:
        yield session


@pytest.fixture(scope="session")
async def create_test_user():
    async with async_session() as session:
        stmt = select(UserModel).where(UserModel.username == "testuser")
        existing_user = await session.execute(stmt)
        existing_user = existing_user.scalar_one_or_none()
        if not existing_user:
            user_data = UserCreate(
                username="testuser2",
                email="testuser@example.com",
                password="testpassword",
                phone_number="1234567890",
            )
            user = UserModel(**user_data.dict())
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        return existing_user


@pytest.fixture(scope="function")
async def client():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        yield ac


@pytest.mark.asyncio
async def test_login(client, create_test_user):
    login_data = {"username": create_test_user.username, "password": "testpassword"}
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_create_article(client, create_test_user):
    login_data = {"username": create_test_user.username, "password": "testpassword"}
    login_response = await client.post("/auth/token", data=login_data)
    access_token = login_response.json()["access_token"]


    article_data = ArticleCreate(
        title="Test Article",
        category="Test",
        summary_1="Test Summary 1",
        summary_2="Test Summary 2",
        author_id=1,
    )

    response = await client.post(
        "/articles/",
        json=article_data.model_dump(),
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print(response.text)
    assert response.status_code == 201
    assert response.json()["title"] == "Test Article"


@pytest.mark.asyncio
async def test_search_articles(client, create_test_user):
    login_data = {"username": create_test_user.username, "password": "testpassword"}
    login_response = await client.post("/auth/token", data=login_data)
    access_token = login_response.json()["access_token"]

    article_data = ArticleCreate(
        title="Test Article",
        category="Test",
        summary_1="Test Summary 1",
        summary_2="Test Summary 2",
        author_id=1,
    )

    await client.post(
        "/articles/",
        json=article_data.model_dump(),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response = await client.get("/articles/search/", params={"query": "Test Article"})
    print(response.text)
    assert response.status_code == 200
    assert len(response.json()) > 0
