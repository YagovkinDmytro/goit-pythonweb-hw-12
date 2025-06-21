import os
import pytest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from libgravatar import Gravatar
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession 
from main import app
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import create_access_token, Hash
from src.services.auth import get_current_user
import contextlib


load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

POSTGRES_USER_TEST = os.getenv("POSTGRES_USER_TEST")
POSTGRES_PASSWORD_TEST = os.getenv("POSTGRES_PASSWORD_TEST")
POSTGRES_HOST_TEST = os.getenv("POSTGRES_HOST_TEST")
POSTGRES_PORT_TEST = os.getenv("POSTGRES_PORT_TEST")
POSTGRES_DB_TEST = os.getenv("POSTGRES_DB_TEST")

# create docker container
# docker run --name db-test -p 5433:5432 -e POSTGRES_USER="POSTGRES_USER" -e POSTGRES_PASSWORD="POSTGRES_PASSWORD" -e POSTGRES_DB="POSTGRES_DB_TEST" -d postgres

DB_URL = f"postgresql+asyncpg://{POSTGRES_USER_TEST}:{POSTGRES_PASSWORD_TEST}@{POSTGRES_HOST_TEST}:{POSTGRES_PORT_TEST}/{POSTGRES_DB_TEST}"

engine = create_async_engine(
    DB_URL,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "user_name": "Nick",
    "user_email": "test@example.com",
    "password": "123456789",
}


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        avatar = None
        try:
            g = Gravatar(test_user["user_email"])
            avatar = g.get_image()
        except Exception as e:
            pass
        
        hash_password = Hash().get_password_hash(test_user["password"])
        current_user = User(
            user_name=test_user["user_name"],
            user_email=test_user["user_email"],
            hashed_password=hash_password,
            avatar=avatar,
            confirmed=True,
        )
        session.add(current_user)
        await session.flush()
        await session.commit()

        # Let's check if it can be found again from the database
        created = await session.scalar(
            select(User).where(User.user_name == test_user["user_name"])
        )
        
        yield


@pytest_asyncio.fixture(scope="module")
async def client():
    # Dependency override
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def override_get_current_user():
        async with TestingSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.user_name == test_user["user_name"])
            )
            user = result.scalar_one()
            return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="module")
async def get_token():
    token = await create_access_token(data={"sub": test_user["user_name"]})
    return token

@pytest_asyncio.fixture
async def auth_headers(get_token):
    return {"Authorization": f"Bearer {get_token}"}