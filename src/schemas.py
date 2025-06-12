from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class ContactCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="John")
    surname: str = Field(..., min_length=1, max_length=50, example="Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    phone: str = Field(..., min_length=7, max_length=50, example="+00123456789")
    birth_date: date = Field(..., example="1990-01-31")
    extra_info: Optional[str] = Field(None, max_length=255, example="Some additional info")


class ContactResponseModel(ContactCreateModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ContactBirthdayResponseModel(BaseModel):
    id: int
    name: str
    surname: str
    birth_date: date


class ContactPutModel(ContactCreateModel):
    id: int = Field(...)


class ContactPatchModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, example="John")
    surname: Optional[str] = Field(None, min_length=1, max_length=50, example="Doe")
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")
    phone: Optional[str] = Field(None, min_length=7, max_length=50, example="+00123456789")
    birth_date: Optional[date] = Field(None, example="1990-01-31")
    extra_info: Optional[str] = Field(None, max_length=255, example="Some additional info")


# User schemas
class User(BaseModel):
    id: int
    user_name: str
    user_email: EmailStr
    avatar: str

    model_config = ConfigDict(from_attributes=True)

# Schema for registration request
class UserCreate(BaseModel):
    user_name: str
    user_email: EmailStr
    password: str

# Scheme for the token
class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    user_email: EmailStr
