from fastapi import APIRouter, Depends, Request, UploadFile, File

from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import User
from src.services.auth import get_current_user
from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.services.upload_file import UploadFileService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/me", response_model=User, description="No more than 5 requests per minute")
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieves the current user's information.
    Args:
        request (Request): The incoming request.
        user (User): The current user, obtained from the authentication token. Defaults to Depends(get_current_user).
    Returns:
        User: The current user's information.
    """
    return user

@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates a user's avatar by uploading the provided file and updating the user's avatar URL in the database.
    Args:
        file (UploadFile): The file to be uploaded as the user's avatar. Defaults to File().
        user (User): The user whose avatar is being updated, obtained from the authentication token. Defaults to Depends(get_current_user).
        db (AsyncSession): The asynchronous database session. Defaults to Depends(get_db).
    Returns:
        User: The user with the updated avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.user_name)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.user_email, avatar_url)

    return user
