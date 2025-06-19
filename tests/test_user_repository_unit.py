import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1, 
        user_name="testuser", 
        user_email="test@example.com", 
        hashed_password="hashed_pw",
        avatar="avatar.png",
        confirmed=False,
    )


@pytest.fixture
def user_create():
    return UserCreate(
        user_name="testuser", 
        user_email="test@example.com",
        password="secret_password"
    )


@pytest.mark.asyncio
async def test_get_user_by_id(mock_session, user_repository, user):
    # Setup mock
    user_id = user.id
    expected_user = user

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Call method
    result = await user_repository.get_user_by_id(user_id)

    # Assertions
    assert result is not None
    assert result.id == expected_user.id
    mock_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mock_session, user_repository):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Call method
    result = await user_repository.get_user_by_id(777)

    # Assertions
    assert result is None
    mock_session.execute.assert_awaited()
    

@pytest.mark.asyncio
async def test_get_user_by_user_name(mock_session, user_repository, user):
    # Setup mock
    user_name = user.user_name
    expected_user = user

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_user_name(user_name)
    
    # Assertions
    assert result is not None
    assert result.user_name == expected_user.user_name
    mock_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_user_by_user_name_not_found(mock_session, user_repository):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_user_name("George")
    
    # Assertions
    assert result is None
    mock_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_user_by_user_email(mock_session, user_repository, user):
    # Setup mock
    user_email = user.user_email
    expected_user = user

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_user_email(user_email)
    
    # Assertions
    assert result is not None
    assert result.user_email == expected_user.user_email
    mock_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_user_by_user_email_not_found(mock_session, user_repository):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_user_by_user_email("not_exist@example.com")
    
    # Assertions
    assert result is None
    mock_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_create_user(mock_session, user_repository, user, user_create):
    # Setup mock
    user_data = user_create

    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def refresh_side_effect(user):
        user.id = 1
        user.avatar="avatar.png" 

    mock_session.refresh.side_effect = refresh_side_effect
    
    # Call method
    result = await user_repository.create_user(user_data, avatar=None)
    
    # Assertions
    assert result.id == 1
    assert result.user_name == user_data.user_name
    assert result.user_email == user_data.user_email
    assert result.hashed_password == user_data.password
    assert result.avatar == "avatar.png"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_confirmed_user_email(mock_session, user_repository, user):
    # Setup mock
    user.confirmed = False
    user_email = user.user_email

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    # Call method
    await user_repository.confirmed_user_email(user_email)

    # Assertions
    assert user.confirmed is True
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_avatar_url(mock_session, user_repository, user):
    # Setup mock
    email = user.user_email
    new_avatar_url = "https://new.avatar/url.png"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Call method
    result = await user_repository.update_avatar_url(email, new_avatar_url)

    # Assertions
    assert result.avatar == new_avatar_url
    assert result is user
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)
