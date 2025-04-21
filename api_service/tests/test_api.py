import pytest, httpx
from src.main import recommend, UserIn

@pytest.mark.asyncio
async def test_recommend(monkeypatch):
    async def fake_post(url, json):
        return httpx.Response(200, json={"items": ["demo"]})
    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)
    resp = await recommend(UserIn(user_id=1))
    assert resp["items"] == ["demo"]
