from datetime import datetime
from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/comment/create",
        json={"post_id": 1, "text": "tu est une fleur"},
    )
    assert response.status_code == 201

    response = await client.get("/comment/read_all")
    assert response.status_code == 200

    print(response.json())
    assert response.json().get("items")[0].get("id") == 1
    assert response.json().get("items")[0].get("user_id") == 1
    assert response.json().get("items")[0].get("post_id") == 1
    assert response.json().get("items")[0].get("text") == "tu est une fleur"
    timestamp_str = response.json().get("items")[0].get("timestamp")
    # Verify it is a string and can be parsed as a datetime
    assert isinstance(timestamp_str, str)
    assert datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

@pytest.mark.asyncio
async def test(client: AsyncClient):
    assert True