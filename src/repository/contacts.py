from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import extract, or_
from datetime import datetime, timedelta
from src.database.models import Contact, User
from src.schemas import ContactCreateModel, ContactPutModel, ContactPatchModel

class ContactRepository:
    def __init__(self, session: AsyncSession):
        """
        Initializes a new instance of the ContactRepository class.
            
        Args:
            session (AsyncSession): The asynchronous database session.
        """
        self.db = session

    async def create_contact(self, body: ContactCreateModel, user: User) -> Contact:
        """
        Creates a new contact in the database.
        Args:
            body (ContactCreateModel): The contact data to be created.
            user (User): The user who owns the contact.
        Returns:
            Contact: The newly created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact


    async def get_contacts(
            self,
            user: User,
            skip: int,
            limit: int,
            name: Optional[str] = None,
            surname: Optional[str] = None,
            email: Optional[str] = None,
    ) -> List[Contact]:
        """
        Retrieves a list of contacts from the database based on the provided filters.
        
        Args:
            user (User): The user who owns the contacts.
            skip (int): The number of contacts to skip before starting to return records.
            limit (int): The maximum number of contacts to return.
            name (Optional[str], optional): The name of the contact to filter by. Defaults to None.
            surname (Optional[str], optional): The surname of the contact to filter by. Defaults to None.
            email (Optional[str], optional): The email of the contact to filter by. Defaults to None.
        
        Returns:
            List[Contact]: A list of contacts that match the provided filters.
        """
        stmt = select(Contact).where(Contact.user_id == user.id)

        if name:
            stmt = stmt.where(Contact.name.ilike(f"%{name}%"))
        if surname:
            stmt = stmt.where(Contact.surname.ilike(f"%{surname}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
        
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    

    async def get_contacts_for_birthdays(self, user: User, days_limit: int = 7) -> List[Contact]:
        """
        Retrieves a list of contacts from the database whose birthdays fall within a specified range of days.
        Args:
            user (User): The user who owns the contacts.
            days_limit (int, optional): The number of days to look ahead for upcoming birthdays. Defaults to 7.
        Returns:
            List[Contact]: A list of contacts whose birthdays are within the specified range.
        """
        today = datetime.today().date()
        end_date = today + timedelta(days=days_limit)
        start_month, start_day = today.month, today.day
        end_month, end_day = end_date.month, end_date.day
        stmt = select(Contact).where(Contact.user==user)
        if start_month == end_month:
            stmt = stmt.where(
                extract('month', Contact.birth_date) == start_month,
                extract('day', Contact.birth_date).between(start_day, end_day)
            )
        else:
            stmt = stmt.where(
                or_(
                    (
                        (extract('month', Contact.birth_date) == start_month) &
                        (extract('day', Contact.birth_date) >= start_day)
                    ),
                    (
                        (extract('month', Contact.birth_date) == end_month) &
                        (extract('day', Contact.birth_date) <= end_day)
                    )
                )
            )
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieves a contact from the database by its ID and the user who owns it.
        
        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user who owns the contact.
        
        Returns:
            Contact | None: The contact with the specified ID, or None if no contact is found.
        """
        stmt = select(Contact).where(Contact.id == contact_id, Contact.user==user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()
    
    async def put_contact(self, contact_id: int, body: ContactPutModel, user: User) -> Contact | None:
        """
        Updates an existing contact in the database.
        
        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactPutModel): The updated contact data.
            user (User): The user who owns the contact.
        
        Returns:
            Contact | None: The updated contact, or None if no contact is found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def patch_contact(self, contact_id: int, body: ContactPatchModel, user: User) -> Contact | None:
        """
        Updates an existing contact in the database partially.
        
        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactPatchModel): The updated contact data.
            user (User): The user who owns the contact.
        
        Returns:
            Contact | None: The updated contact, or None if no contact is found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def delete_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Deletes a contact from the database.
        
        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user who owns the contact.
        
        Returns:
            Contact | None: The deleted contact, or None if no contact is found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
