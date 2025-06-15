from datetime import date
from typing import List
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactCreateModel, ContactResponseModel, ContactBirthdayResponseModel, ContactPutModel, ContactPatchModel
from src.services.contacts import ContactService
from src.services.auth import get_current_user


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactCreateModel, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreateModel, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Creates a new contact in the database.
    Args:
        body (ContactCreateModel): The contact data to be created.
        db (AsyncSession): The database session. Defaults to Depends(get_db).
        user (User): The user who owns the contact. Defaults to Depends(get_current_user).
    Returns:
        ContactCreateModel: The newly created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.get("/", response_model=List[ContactResponseModel])
async def read_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    surname: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves a list of contacts from the database based on the provided filters.
    Args:
        skip (int): The number of contacts to skip before starting to return records.
        limit (int): The maximum number of contacts to return.
        name (Optional[str]): The name of the contact to filter by.
        surname (Optional[str]): The surname of the contact to filter by.
        email (Optional[str]): The email of the contact to filter by.
        db (AsyncSession): The asynchronous database session.
        user (User): The user who owns the contacts.
    Returns:
        List[ContactResponseModel]: A list of contacts that match the provided filters.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, name, surname, email, user)
    return contacts


@router.get("/birthdays", response_model=List[ContactBirthdayResponseModel])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user),
):
    """
    Retrieves a list of contacts with upcoming birthdays.
    Args:
        db (AsyncSession): The asynchronous database session.
        user (User): The user who owns the contacts.
    Returns:
        List[ContactBirthdayResponseModel]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts_upcoming_birthdays(user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponseModel)
async def read_contact(
    contact_id: int = Path(description="The ID of the contact to get", ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves a contact from the database by its ID.
    
    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The asynchronous database session.
        user (User): The user who owns the contact.
    
    Returns:
        ContactResponseModel: The retrieved contact, or raises a 404 error if not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.put("/{contact_id}", response_model=ContactPutModel)
async def update_contact(
    body: ContactPutModel,
    contact_id: int = Path(description="The ID of the contact to put", ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Updates an existing contact in the database.
    Args:
        body (ContactPutModel): The updated contact data.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The asynchronous database session.
        user (User): The user who owns the contact.
    Returns:
        ContactPutModel: The updated contact, or raises a 404 error if not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.put_contact(contact_id, body, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )
    return contact


@router.patch("/{contact_id}", response_model=ContactPatchModel)
async def update_contact(
    body: ContactPatchModel,
    contact_id: int = Path(description="The ID of the contact to patch", ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Updates an existing contact in the database partially.
    
    Args:
        body (ContactPatchModel): The updated contact data.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The asynchronous database session.
        user (User): The user who owns the contact.
    
    Returns:
        ContactPatchModel: The updated contact, or raises a 404 error if not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.patch_contact(contact_id, body, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int = Path(description="The ID of the contact to delete", ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Deletes a contact from the database by its ID.
    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The asynchronous database session.
        user (User): The user who owns the contact.
    Returns:
        The deleted contact, or raises a 404 error if not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact