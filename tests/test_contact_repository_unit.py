import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactCreateModel, ContactPutModel, ContactPatchModel
from datetime import date, timedelta


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1, 
        user_name="testuser", 
        user_email="test@example.com", 
        avatar="avatar.png"
    )


@pytest.fixture
def contacts(user):
    contact1 = Contact(
        id=1, 
        name="Niko", 
        surname="Man", 
        email="niko.man@example.com", 
        phone="+00123456789", 
        birth_date=date(1990, 1, 1), 
        user_id=user.id
    )
    contact2 = Contact(
        id=2, 
        name="Don", 
        surname="Rock", 
        email="don.rock@example.com", 
        phone="+00123456799", 
        birth_date=date(1992, 2, 2), 
        user_id=user.id
    )
    return [contact1, contact2]

@pytest.fixture
def contact(user):
    contact1 = Contact(
        id=1, 
        name="Niko", 
        surname="Man", 
        email="niko.man@example.com", 
        phone="+00123456789", 
        birth_date=date(1990, 1, 1), 
        user_id=user.id
    )
    return [contact1]


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user, contacts):
    # Setup mock
    mock_result = MagicMock()
    # Mock the result of execution execute
    mock_result.scalars.return_value.all.return_value = contacts
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Calling the get_contacts method
    result = await contact_repository.get_contacts(user=user, skip=0, limit=10)
    
    # Assert that a list of 2 contacts was returned
    assert len(result) == 2
    assert result[0].name == "Niko"
    assert result[1].name == "Don"

    # Check that mock_session.execute was called at least once
    mock_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_contacts_filter_by_name(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Call method
    result = await contact_repository.get_contacts(user=user, skip=0, limit=10, name="Niko")
    
    # Assertions
    assert len(result) == 1
    assert result[0].name == "Niko"


@pytest.mark.asyncio
async def test_get_contacts_filter_by_surname(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Call method
    result = await contact_repository.get_contacts(user=user, skip=0, limit=10, surname="Man")
    
    # Assertions
    assert len(result) == 1
    assert result[0].surname == "Man"


@pytest.mark.asyncio
async def test_get_contacts_filter_by_email(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Call method
    result = await contact_repository.get_contacts(user=user, skip=0, limit=10, email="niko.man@example.com")
    
    # Assertions
    assert len(result) == 1
    assert result[0].email == "niko.man@example.com"


@pytest.mark.asyncio
async def test_get_contact_by_id_found(contact_repository, mock_session, user, contact):
    # Setup
    contact_id = contact[0].id
    expected_contact = contact[0]

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contact_by_id(contact_id, user=user)
    
    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.name == "Niko"
    assert result == expected_contact
    mock_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(contact_repository, mock_session, user):
    # Setup
    contact_id = 777

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contact_by_id(contact_id, user=user)
    
    # Assertions
    assert result is None
    mock_session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactCreateModel(
        name="Niko",
        surname="Man",
        email="niko.man@example.com",
        phone="+00123456789",
        birth_date=date(1990, 1, 1),
        extra_info="Some additional info"
    )

    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def refresh_side_effect(contact):
        contact.id = 1
        contact.user_id = user.id

    mock_session.refresh.side_effect = refresh_side_effect

    # Call method
    result = await contact_repository.create_contact(contact_data, user)

    # Assertions
    assert result.id == 1
    assert result.name == contact_data.name
    assert result.surname == contact_data.surname
    assert result.email == contact_data.email
    assert result.phone == contact_data.phone
    assert result.birth_date == contact_data.birth_date
    assert result.extra_info == contact_data.extra_info
    assert result.user_id == user.id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_get_contacts_for_birthdays(contact_repository, mock_session, user, contacts):
    # Setup mock
    today = date.today()
    upcoming_birth = today + timedelta(days=3)

    contacts[0].birth_date = upcoming_birth
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contacts[0]]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contacts_for_birthdays(user=user, days_limit=7)

    # Assertions
    assert len(result) == 1
    assert result[0].id == contacts[0].id
    assert result[0].birth_date == upcoming_birth
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_put_contact_found(contact_repository, mock_session, user, contacts):
    # Setup mock
    contact_to_update = contacts[0]

    contact_repository.get_contact_by_id = AsyncMock(return_value=contact_to_update)

    updated_data = ContactPutModel(
        id=contact_to_update.id,
        name="Updated Name", 
        surname="Updated Surname", 
        email="updated.email@example.com",
        phone="+00123456789",
        birth_date=date(1990, 1, 31),
        extra_info="Some additional info"
    )

    # Call method
    result = await contact_repository.put_contact(contact_id=contact_to_update.id, body=updated_data, user=user)

    # Assertions
    assert result is not None
    assert result.name == updated_data.name
    assert result.surname == updated_data.surname
    assert result.email == updated_data.email
    assert result.phone == updated_data.phone
    assert result.birth_date == updated_data.birth_date
    assert result.extra_info == updated_data.extra_info
    assert result.user_id == user.id
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact_to_update)


@pytest.mark.asyncio
async def test_put_contact_not_found(contact_repository, mock_session, user, contacts):
    # Setup mock
    contact_repository.get_contact_by_id = AsyncMock(return_value=None)

    updated_data = ContactPutModel(
        id=777,
        name="Updated Name", 
        surname="Updated Surname", 
        email="updated.email@example.com",
        phone="+00123456789",
        birth_date=date(1990, 1, 31),
        extra_info="Some additional info"
    )

    # Call method
    result = await contact_repository.put_contact(contact_id=777, body=updated_data, user=user)
    
    # Assertions
    assert result is None
    mock_session.commit.assert_not_awaited()
    mock_session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_patch_contact_found(contact_repository, mock_session, user, contacts):
    # Setup mock
    contact_to_patch = contacts[0]

    contact_repository.get_contact_by_id = AsyncMock(return_value=contact_to_patch)

    patch_data = ContactPatchModel(
        id=contact_to_patch.id,
        email="new.email@example.com",
        extra_info="Updated info"
    )

    # Call method
    result = await contact_repository.patch_contact(contact_id=contact_to_patch.id, body=patch_data, user=user)

    # Assertions
    assert result is not None
    assert result.email == "new.email@example.com"
    assert result.extra_info == "Updated info"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact_to_patch)


@pytest.mark.asyncio
async def test_patch_contact_not_found(contact_repository, mock_session, user, contacts):
    # Setup mock
    contact_repository.get_contact_by_id = AsyncMock(return_value=None)

    patch_data = ContactPatchModel(
        id=777,
        email="new.email@example.com",
        extra_info="Updated info"
    )

    # Call method
    result = await contact_repository.patch_contact(contact_id=777, body=patch_data, user=user)

    # Assertions
    assert result is None
    mock_session.commit.assert_not_awaited()
    mock_session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_contact_found(contact_repository, mock_session, user, contacts):
    # Setup mock
    contact_to_delete = contacts[0]

    contact_repository.get_contact_by_id = AsyncMock(return_value=contact_to_delete)
    # Call method
    result = await contact_repository.delete_contact(contact_id=contact_to_delete.id, user=user)

    # Assertions
    assert result == contact_to_delete
    mock_session.commit.assert_awaited_once()
    mock_session.delete.assert_awaited_once_with(contact_to_delete)


@pytest.mark.asyncio
async def test_delete_contact_not_found(contact_repository, mock_session, user):
    # Setup mock
    contact_repository.get_contact_by_id = AsyncMock(return_value=None)
    
    # Call method
    result = await contact_repository.delete_contact(contact_id=777, user=user)

    # Assertions
    assert result is None
    mock_session.commit.assert_not_awaited()
    mock_session.delete.assert_not_awaited()
