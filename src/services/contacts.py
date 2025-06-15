from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.repository.contacts import ContactRepository, User
from src.schemas import ContactCreateModel, ContactPutModel, ContactPatchModel

def _handle_integrity_error(e: IntegrityError):
    """
    Handles integrity errors that occur during database operations.
    Args:
        e (IntegrityError): The integrity error that occurred.
    Raises:
        HTTPException: A 409 Conflict exception if a contact with the same email already exists.
        HTTPException: A 400 Bad Request exception for any other data integrity error.
    """
    if "contacts_email_key" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A contact with this email already exists.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data integrity error.",
        )

class ContactService:
    def __init__(self, db: AsyncSession):
        """
        Initializes a new instance of the ContactService class.
        
        Args:
            db (AsyncSession): The asynchronous database session.
        
        Returns:
            None
        """
        self.repository = ContactRepository(db)


    async def create_contact(self, body: ContactCreateModel, user: User):
        """
        Creates a new contact in the database.
        
        Args:
            body (ContactCreateModel): The contact data to be created.
            user (User): The user who owns the contact.
        
        Returns:
            The newly created contact.
        """
        try:
            return await self.repository.create_contact(body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    # the order of arguments to repository.get_contacts matters
    async def get_contacts(self, skip: int, limit: int, name: str, surname: str, email: str, user: User):
        """
        Retrieves a list of contacts from the database based on the provided filters.
        
        Args:
            skip (int): The number of contacts to skip before starting to return records.
            limit (int): The maximum number of contacts to return.
            name (str): The name of the contact to filter by.
            surname (str): The surname of the contact to filter by.
            email (str): The email of the contact to filter by.
            user (User): The user who owns the contacts.
        
        Returns:
            List[Contact]: A list of contacts that match the provided filters.
        """
        return await self.repository.get_contacts(user, skip, limit, name, surname, email)
    

    async def get_contacts_upcoming_birthdays(self, user: User):
        """
        Retrieves a list of contacts with upcoming birthdays.
        
        Args:
            user (User): The user who owns the contacts.
        
        Returns:
            List[Contact]: A list of contacts whose birthdays are within the specified range.
        """
        return await self.repository.get_contacts_for_birthdays(user)


    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieves a contact from the database by its ID and the user who owns it.
        
        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user who owns the contact.
        
        Returns:
            The contact with the specified ID, or None if no contact is found.
        """
        return await self.repository.get_contact_by_id(contact_id, user)


    async def put_contact(self, contact_id: int, body: ContactPutModel, user: User):
        """
        Updates an existing contact in the database.
        
        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactPutModel): The updated contact data.
            user (User): The user who owns the contact.
        
        Returns:
            The updated contact.
        """
        try:
            return await self.repository.put_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)
    

    async def patch_contact(self, contact_id: int, body: ContactPatchModel, user: User):
        """
        Updates an existing contact in the database partially.
        
        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactPatchModel): The updated contact data.
            user (User): The user who owns the contact.
        
        Returns:
            The updated contact.
        """
        try:
            return await self.repository.patch_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)


    async def delete_contact(self, contact_id: int, user: User):
        """
        Deletes a contact from the database.
        
        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user who owns the contact.
        
        Returns:
            The deleted contact.
        """
        return await self.repository.delete_contact(contact_id, user)