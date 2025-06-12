from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.repository.contacts import ContactRepository, User
from src.schemas import ContactCreateModel, ContactPutModel, ContactPatchModel

def _handle_integrity_error(e: IntegrityError):
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
        self.repository = ContactRepository(db)


    async def create_contact(self, body: ContactCreateModel, user: User):
        try:
            return await self.repository.create_contact(body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    # the order of arguments to repository.get_contacts matters
    async def get_contacts(self, skip: int, limit: int, name: str, surname: str, email: str, user: User):
        return await self.repository.get_contacts(user, skip, limit, name, surname, email)
    

    async def get_contacts_upcoming_birthdays(self, user: User):
        return await self.repository.get_contacts_for_birthdays(user)


    async def get_contact(self, contact_id: int, user: User):
        return await self.repository.get_contact_by_id(contact_id, user)


    async def put_contact(self, contact_id: int, body: ContactPutModel, user: User):
        try:
            return await self.repository.put_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)
    

    async def patch_contact(self, contact_id: int, body: ContactPatchModel, user: User):
        try:
            return await self.repository.patch_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)


    async def delete_contact(self, contact_id: int, user: User):
        return await self.repository.delete_contact(contact_id, user)