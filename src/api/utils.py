from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Handles a GET request to the '/healthchecker' endpoint to check the health of the database connection.
    Args:
        db (AsyncSession): The asynchronous database session, provided by the get_db dependency.
    Returns:
        dict: A JSON response with a message indicating the health of the database connection.
    Raises:
        HTTPException: If the database is not configured correctly or if there is an error connecting to the database.
    """
    try:
        # Виконуємо асинхронний запит
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
