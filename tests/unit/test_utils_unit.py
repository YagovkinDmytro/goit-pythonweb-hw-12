import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from src.api.utils import healthchecker


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_healthchecker_success(mock_db):
    # Setup: mock db.execute to return a result with scalar_one_or_none() returning 1
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = 1
    mock_db.execute.return_value = mock_result

    # Call endpoint
    response = await healthchecker(db=mock_db)

    # Assertions
    assert response == {"message": "Welcome to FastAPI!"}
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_healthchecker_no_result(mock_db):
    # Setup: mock db.execute to return None as scalar_one_or_none()
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Expect HTTPException due to failed health check
    with pytest.raises(HTTPException) as exc_info:
        await healthchecker(db=mock_db)

    # Assertions
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error connecting to the database"
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_healthchecker_raises_exception(mock_db):
    # Setup: simulate a database error
    mock_db.execute.side_effect = Exception("Database error")

    # Expect HTTPException due to exception
    with pytest.raises(HTTPException) as exc_info:
        await healthchecker(db=mock_db)

    # Assertions
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error connecting to the database"
    mock_db.execute.assert_awaited_once()