from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from src.schemas import UserCreate

class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initializes a new instance of the UserRepository class.
        
        Args:
            session (AsyncSession): The asynchronous database session.
        """
        self.db = session
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieves a user from the database by their ID.
        Args:
            user_id (int): The ID of the user to retrieve.
        Returns:
            User | None: The user with the specified ID, or None if no user is found.
        """
        stmt = select(User).where(User.id == user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_user_name(self, user_name: str) -> User | None:
        """
        Retrieves a user from the database by their username.
        
        Args:
            user_name (str): The username of the user to retrieve.
        
        Returns:
            User | None: The user with the specified username, or None if no user is found.
        """
        stmt = select(User).where(User.user_name == user_name)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()
    
    async def get_user_by_user_email(self, user_email: str) -> User | None:
        """
        Retrieves a user from the database by their email address.
        
        Args:
            user_email (str): The email address of the user to retrieve.
        
        Returns:
            User | None: The user with the specified email address, or None if no user is found.
        """
        stmt = select(User).where(User.user_email == user_email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()
    
    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Creates a new user in the database.
        Args:
            body (UserCreate): The user data to be created.
            avatar (str, optional): The avatar URL of the user. Defaults to None.
        Returns:
            User: The newly created user.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def confirmed_user_email(self, user_email: str) -> None:
        """
        Confirms a user's email address by updating the user's confirmed status in the database.
        Args:
            user_email (str): The email address of the user to confirm.
        Returns:
            None
        """
        user = await self.get_user_by_user_email(user_email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Updates a user's avatar URL in the database.
        
        Args:
            email (str): The email address of the user to update.
            url (str): The new avatar URL.
        
        Returns:
            User: The user with the updated avatar URL.
        """
        user = await self.get_user_by_user_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
    