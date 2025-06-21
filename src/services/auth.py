from datetime import datetime, timedelta, UTC
from typing import Optional
import json
import redis

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService


r = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)

class Hash:
    """
    A utility class for hashing and verifying passwords using bcrypt.
    
    Uses passlib's CryptContext for secure password hashing.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify that a plain password matches its hashed version.
        Args:
            plain_password (str): The plain-text password provided by the user.
            hashed_password (str): The hashed password stored in the database.
        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generates a hashed version of a given password using bcrypt.
        Args:
            password (str): The plain-text password to be hashed.
        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# define a function to generate a new access token
async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Generates a new access token based on the provided data and expiration time.

    Args:
        data (dict): The data to be encoded in the access token.
        expires_delta (Optional[int]): The time in seconds until the token expires. Defaults to None.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the current user based on the provided token and database session.

    Args:
        token (str): The authentication token to validate. Defaults to Depends(oauth2_scheme).
        db (AsyncSession): The database session to use for user retrieval. Defaults to Depends(get_db).

    Returns:
        User: The current user if the token is valid, otherwise raises an HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    
    try:
        cached = r.get(f"user:{username}")
        print("Checking cache:", cached)
    except Exception as e:
        print("Error accessing cache:", e)
        cached = None
    
    user_service = UserService(db)

    if cached:
        try:
            user_data = json.loads(cached)
            user_id = user_data.get("id")
            print("user_id", user_id)
            
            if user_id:
                user = await user_service.get_user_by_id(user_id)
                print("user1", user)
        except Exception as e:
            print(f"ОError deserializing data from cache: {e}")
            user = None
    else:
        print("Cache not found - loading from DB")
        user = await user_service.get_user_by_user_name(username)
        print("user2", user)
        if user:
            safe_data = {
            "id": user.id,
            "user_name": user.user_name,
            "email": user.user_email,
            "avatar": user.avatar,
        }
            
        try:
            success = r.set(f"user:{username}", json.dumps(safe_data))
            print("Redis SET success:", success)
            r.expire(f"user:{username}", 900)
        except Exception as e:
            print(f"Error writing to Redis: {e}")
    
    # need to get user from db for test
    # user_service = UserService(db)
    # user = await user_service.get_user_by_user_name(username)

    if user is None:
        raise credentials_exception
        
    return user


async def create_email_token(data: dict):
    """
    Generates a new email verification token based on the provided data and expiration time.
    
    Args:
        data (dict): The data to be encoded in the email token.
    
    Returns:
        str: The encoded JWT email token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Retrieves the email address from a given email verification token.

    Args:
        token (str): The email verification token to decode.

    Returns:
        str: The email address associated with the token.

    Raises:
        HTTPException: If the token is invalid or cannot be decoded.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email verification token",
        )
    