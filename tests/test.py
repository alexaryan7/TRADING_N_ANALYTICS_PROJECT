import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_fails_with_invalid_credentials(async_client: AsyncClient):

    payload = {
        "email": "hacker@example.com",
        "password": "wrongpassword123"
    }
    
    response = await async_client.post("/api/auth/login", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."