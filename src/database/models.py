from datetime import datetime
from datetime import date
from typing import Optional, List
from sqlalchemy import text
from sqlalchemy import Integer, String, Date, DateTime, Boolean, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.sql.schema import ForeignKey


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Contact(Base):
    """
    SQLAlchemy model representing a contact entity.

    Attributes:
        id (int): Primary key.
        name (str): First name of the contact.
        surname (str): Last name of the contact.
        email (str): Unique email address of the contact.
        phone (str): Phone number of the contact.
        birth_date (date): Date of birth.
        extra_info (Optional[str]): Additional information about the contact.
        user_id (int): ID of the user who owns this contact.
        user (User): The related user instance (owner).
    """
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    phone: Mapped[str] = mapped_column(String(50))
    birth_date: Mapped[date] = mapped_column(Date)
    extra_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="contacts")

    def __repr__(self):
        """
        Returns a string representation of the Contact object.
        
        The string representation includes the name and email of the contact.
        
        Returns:
            str: A string representation of the Contact object.
        """
        return f"<Contact(name={self.name}, email={self.email})>"


class User(Base):
    """
    SQLAlchemy model representing a user of the system.

    Attributes:
        id (int): Primary key.
        user_name (str): Unique username.
        user_email (str): Unique email address.
        hashed_password (str): Hashed user password.
        created_at (datetime): Account creation timestamp.
        avatar (str): Optional URL to the user's avatar image.
        confirmed (bool): Whether the user's email is confirmed.
        contacts (List[Contact]): List of user's contacts.
    """
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(50), unique=True)
    user_email: Mapped[str] = mapped_column(String(120), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="user", cascade="all, delete")

    def __repr__(self):
        """
        Returns a string representation of the User object.
        
        The string representation includes the id, username, and email of the user.
        
        Returns:
            str: A string representation of the User object.
        """
        return f"<User(id={self.id}, username={self.user_name}, email={self.user_email})>"
    