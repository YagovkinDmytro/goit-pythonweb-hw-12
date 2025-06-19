from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Initializes a new instance of the UserService class.
        
        Args:
            db (AsyncSession): The asynchronous database session.
        
        Returns:
            None
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user in the database.
        
        Args:
            body (UserCreate): The user data to be created.
        
        Returns:
            The newly created user.
        """
        avatar = None
        try:
            g = Gravatar(body.user_email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        
        return await self.repository.create_user(body, avatar)
    
    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user from the database by their ID.
        
        Args:
            user_id (int): The ID of the user to retrieve.
        
        Returns:
            The user with the specified ID, or None if no user is found.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_user_name(self, user_name: str):
        """
        Retrieves a user from the database by their username.
        
        Args:
            user_name (str): The username of the user to retrieve.
        
        Returns:
            The user with the specified username, or None if no user is found.
        """
        return await self.repository.get_user_by_user_name(user_name)

    async def get_user_by_user_email(self, user_email: str):
        """
        Retrieves a user from the database by their email address.
        
        Args:
            user_email (str): The email address of the user to retrieve.
        
        Returns:
            The user with the specified email address, or None if no user is found.
        """
        return await self.repository.get_user_by_user_email(user_email)
    
    async def confirmed_user_email(self, user_email: str):
        """
        Confirms a user's email address by updating the user's confirmed status in the database.
        
        Args:
            user_email (str): The email address of the user to confirm.
        
        Returns:
            None
        """
        return await self.repository.confirmed_user_email(user_email)
    
    async def update_avatar_url(self, email: str, url: str):
        """
        Updates a user's avatar URL in the database.
        
        Args:
            email (str): The email address of the user to update.
            url (str): The new avatar URL.
        
        Returns:
            The user with the updated avatar URL.
        """
        return await self.repository.update_avatar_url(email, url)
    