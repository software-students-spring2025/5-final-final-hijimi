import pytest
from main import app
from api.recommender_client import recommend_by_user_history


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_recommend_success(client):
    response = client.get("/recommend/u1")
    assert response.status_code == 200
    data = response.get_json()
    assert "user_id" in data
    assert data["user_id"] == "u1"
    assert isinstance(data["recommendations"], list)


def test_recommend_not_found(client):
    response = client.get("/recommend/nonexistent_user")
    assert response.status_code == 200
    data = response.get_json()
    assert data["recommendations"] == []
    assert "message" in data
