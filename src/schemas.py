from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class ContactCreateModel(BaseModel):
    """
    Schema for creating a new contact.

    Attributes:
        name (str): First name of the contact.
        surname (str): Last name of the contact.
        email (EmailStr): Email address of the contact.
        phone (str): Phone number of the contact.
        birth_date (date): Birth date of the contact.
        extra_info (Optional[str]): Additional optional information.
    """
    name: str = Field(..., min_length=1, max_length=50, example="John")
    surname: str = Field(..., min_length=1, max_length=50, example="Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    phone: str = Field(..., min_length=7, max_length=50, example="+00123456789")
    birth_date: date = Field(..., example="1990-01-31")
    extra_info: Optional[str] = Field(None, max_length=255, example="Some additional info")


class ContactResponseModel(ContactCreateModel):
    """
    Schema for returning contact information with an ID.

    Inherits from:
        ContactCreateModel

    Attributes:
        id (int): Unique identifier of the contact.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)


class ContactBirthdayResponseModel(BaseModel):
    """
    Schema for returning contact birthday reminders.

    Attributes:
        id (int): Contact ID.
        name (str): First name of the contact.
        surname (str): Last name of the contact.
        birth_date (date): Contact's birth date.
    """
    id: int
    name: str
    surname: str
    birth_date: date


class ContactPutModel(ContactCreateModel):
    """
    Schema for full update (PUT) of a contact.

    Inherits from:
        ContactCreateModel

    Attributes:
        id (int): ID of the contact to be updated.
    """
    id: int = Field(...)


class ContactPatchModel(BaseModel):
    """
    Schema for partial update (PATCH) of a contact.

    All fields are optional.

    Attributes:
        name (Optional[str]): First name.
        surname (Optional[str]): Last name.
        email (Optional[EmailStr]): Email address.
        phone (Optional[str]): Phone number.
        birth_date (Optional[date]): Birth date.
        extra_info (Optional[str]): Additional info.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50, example="John")
    surname: Optional[str] = Field(None, min_length=1, max_length=50, example="Doe")
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")
    phone: Optional[str] = Field(None, min_length=7, max_length=50, example="+00123456789")
    birth_date: Optional[date] = Field(None, example="1990-01-31")
    extra_info: Optional[str] = Field(None, max_length=255, example="Some additional info")


# User schemas
class User(BaseModel):
    """
    Schema for returning basic user information.

    Attributes:
        id (int): User ID.
        user_name (str): Username.
        user_email (EmailStr): Email address.
        avatar (str): URL to the user's avatar.
    """
    id: int
    user_name: str
    user_email: EmailStr
    avatar: str

    model_config = ConfigDict(from_attributes=True)

# Schema for registration request
class UserCreate(BaseModel):
    """
    Schema for user registration request.

    Attributes:
        user_name (str): Username.
        user_email (EmailStr): Email address.
        password (str): User password (plain-text, to be hashed).
    """
    user_name: str
    user_email: EmailStr
    password: str

# Scheme for the token
class Token(BaseModel):
    """
    Schema for access token response.

    Attributes:
        access_token (str): JWT access token.
        token_type (str): Type of the token (e.g., "bearer").
    """
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Schema for sending user email in a request (e.g., for password reset).

    Attributes:
        user_email (EmailStr): Email address of the user.
    """
    user_email: EmailStr
