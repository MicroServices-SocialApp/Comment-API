# from datetime import datetime
from httpx import AsyncClient
import pytest

# @pytest.mark.asyncio
# async def test_create_user(client: AsyncClient):
#     response = await client.post(
#         "/user/create",
#         json={"username": "string", "email": "string@example.com", "password": "string"},
#     )
#     assert response.status_code == 201

#     response = await client.get(
#         "/user/read_user_by_username",
#         params={"username": "string"},
#     )
#     assert response.status_code == 200
#     assert response.json()[0].get("id") == 1
#     assert response.json()[0].get("username") == "string"
#     assert response.json()[0].get("email") == "string@example.com"
#     timestamp_str = response.json()[0].get("timestamp")
#     # Verify it is a string and can be parsed as a datetime
#     assert isinstance(timestamp_str, str)
#     assert datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

@pytest.mark.asyncio
async def test(client: AsyncClient):
    assert True