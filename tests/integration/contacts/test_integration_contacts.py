import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def test_contact(client, auth_headers):
    response = await client.post("api/contacts/", json={
        "name": "John",
        "surname": "Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "birth_date": "1990-01-31"
    }, headers=auth_headers)
    return response.json()


@pytest.mark.asyncio
async def test_create_contact_success(client, auth_headers):
    contact_data = {
        "name": "Nick",
        "surname": "Smith",
        "email": "nick@example.com",
        "phone": "123456789",
        "birth_date": "1992-05-10"
    }

    response = await client.post("/api/contacts/", json=contact_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == contact_data["name"]
    assert data["surname"] == contact_data["surname"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]
    assert data["birth_date"] == contact_data["birth_date"]


# @pytest.mark.asyncio
# async def test_get_contacts_success(client, auth_headers):
#     response = await client.get("/api/contacts/", headers=auth_headers)

#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)
#     assert all("email" in contact for contact in data)


# @pytest.mark.asyncio
# async def test_create_contact_invalid_email(client, auth_headers):
#     contact_data = {
#         "name": "Bob",
#         "surname": "Stone",
#         "email": "invalid-email"
#     }
#     response = await client.post("/api/contacts/", json=contact_data, headers=auth_headers)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_create_contact_missing_required_fields(client, auth_headers):
#     contact_data = {
#         "surname": "Stone"
#         # no name and email
#     }
#     response = await client.post("/api/contacts/", json=contact_data, headers=auth_headers)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_create_contact_duplicate_email(client, auth_headers):
#     contact_data = {
#         "name": "John",
#         "surname": "Doe",
#         "email": "duplicate@example.com"
#     }

#     first = await client.post("/api/contacts/", json=contact_data, headers=auth_headers)
#     assert first.status_code == 201

#     second = await client.post("/api/contacts/", json=contact_data, headers=auth_headers)
#     assert second.status_code == 409



# @pytest.mark.asyncio
# async def test_get_contact_by_id_success(client, auth_headers):
#     contact_data = {
#         "name": "Nick",
#         "surname": "Smith",
#         "email": "nick@example.com",
#         "phone": "123456789",
#         "birth_date": "1992-05-10"
#     }
#     create_resp = await client.post("/api/contacts/", json=contact_data, headers=auth_headers)
#     contact_id = create_resp.json()["id"]

#     response = await client.get(f"/contacts/{contact_id}", headers=auth_headers)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == contact_id
#     assert data["email"] == contact_data["email"]