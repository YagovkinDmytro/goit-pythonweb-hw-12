from datetime import datetime
from datetime import date
from typing import Optional, List
from sqlalchemy import text
from sqlalchemy import Integer, String, Date, DateTime, Boolean, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.sql.schema import ForeignKey


class Base(DeclarativeBase):
    pass


class Contact(Base):
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
        return f"<Contact(name={self.name}, email={self.email})>"


class User(Base):
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
        return f"<User(id={self.id}, username={self.user_name}, email={self.user_email})>"
    