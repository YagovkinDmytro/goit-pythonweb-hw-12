import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError

from src.services.contacts import ContactService, _handle_integrity_error
from src.schemas import ContactCreateModel, ContactPutModel, ContactPatchModel, User
from datetime import date

class FakeOrig:
    def __str__(self):
        return "duplicate key value violates unique constraint contacts_email_key"

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.rollback = AsyncMock()
    return db


@pytest.fixture
def contact_service(mock_db):
    return ContactService(db=mock_db)


@pytest.fixture
def user():
    return User(
        id=1,
        user_name="testuser",
        user_email="test@example.com",
        avatar="avatar.png"
    )


@pytest.fixture
def contact_create_data():
    return ContactCreateModel(
        name="Alice",
        surname="Smith",
        email="alice@example.com",
        phone="+123456789",
        birth_date=date(1990, 5, 1),
        extra_info="Test note"
    )


@pytest.mark.asyncio
async def test_create_contact_success(contact_service, mock_db, contact_create_data, user):
    contact_service.repository.create_contact = AsyncMock(return_value="created_contact")

    result = await contact_service.create_contact(contact_create_data, user)

    assert result == "created_contact"
    contact_service.repository.create_contact.assert_awaited_once_with(contact_create_data, user)


@pytest.mark.asyncio
async def test_create_contact_integrity_error(contact_service, mock_db, contact_create_data, user):
    error = IntegrityError("Mock", {}, FakeOrig())
    contact_service.repository.create_contact = AsyncMock(side_effect=error)

    with pytest.raises(Exception) as exc_info:
        await contact_service.create_contact(contact_create_data, user)

    assert exc_info.value.status_code == 409
    assert "email already exists" in str(exc_info.value.detail)
    mock_db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_contacts(contact_service, user):
    contact_service.repository.get_contacts = AsyncMock(return_value=["contact1", "contact2"])

    result = await contact_service.get_contacts(skip=0, limit=10, name="Alice", surname="", email="", user=user)

    assert result == ["contact1", "contact2"]
    contact_service.repository.get_contacts.assert_awaited_once_with(user, 0, 10, "Alice", "", "")


@pytest.mark.asyncio
async def test_get_contact(contact_service, user):
    contact_service.repository.get_contact_by_id = AsyncMock(return_value="some_contact")

    result = await contact_service.get_contact(contact_id=1, user=user)

    assert result == "some_contact"
    contact_service.repository.get_contact_by_id.assert_awaited_once_with(1, user)


@pytest.mark.asyncio
async def test_get_contacts_upcoming_birthdays(contact_service, user):
    contact_service.repository.get_contacts_for_birthdays = AsyncMock(return_value=["b1", "b2"])

    result = await contact_service.get_contacts_upcoming_birthdays(user=user)

    assert result == ["b1", "b2"]
    contact_service.repository.get_contacts_for_birthdays.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_put_contact_success(contact_service, user):
    body = ContactPutModel(
        id=1,
        name="Alice",
        surname="Smith",
        email="alice@example.com",
        phone="+123456789",
        birth_date=date(1990, 5, 1),
        extra_info="updated"
    )
    contact_service.repository.put_contact = AsyncMock(return_value="updated_contact")

    result = await contact_service.put_contact(contact_id=1, body=body, user=user)

    assert result == "updated_contact"
    contact_service.repository.put_contact.assert_awaited_once_with(1, body, user)


@pytest.mark.asyncio
async def test_patch_contact_success(contact_service, user):
    body = ContactPatchModel(email="new@example.com", extra_info="new")
    contact_service.repository.patch_contact = AsyncMock(return_value="patched_contact")

    result = await contact_service.patch_contact(contact_id=1, body=body, user=user)

    assert result == "patched_contact"
    contact_service.repository.patch_contact.assert_awaited_once_with(1, body, user)


@pytest.mark.asyncio
async def test_patch_contact_integrity_error(contact_service, mock_db, user):
    body = ContactPatchModel(email="conflict@example.com")
    error = IntegrityError("Mock", {}, FakeOrig())
    contact_service.repository.patch_contact = AsyncMock(side_effect=error)

    with pytest.raises(Exception) as exc_info:
        await contact_service.patch_contact(contact_id=1, body=body, user=user)

    assert exc_info.value.status_code == 409
    mock_db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_contact(contact_service, user):
    contact_service.repository.delete_contact = AsyncMock(return_value="deleted")

    result = await contact_service.delete_contact(contact_id=5, user=user)

    assert result == "deleted"
    contact_service.repository.delete_contact.assert_awaited_once_with(5, user)


def test_handle_integrity_error_duplicate_email():
    err = IntegrityError("mock", {}, FakeOrig())
    with pytest.raises(Exception) as exc_info:
        _handle_integrity_error(err)

    assert exc_info.value.status_code == 409
    assert "email" in str(exc_info.value.detail)


def test_handle_integrity_error_other():
    err = IntegrityError("mock", {}, MagicMock(orig="some other constraint failed"))
    with pytest.raises(Exception) as exc_info:
        _handle_integrity_error(err)

    assert exc_info.value.status_code == 400
    assert "integrity" in str(exc_info.value.detail)