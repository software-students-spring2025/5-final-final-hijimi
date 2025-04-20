from main import app

def test_recommend():
    client = app.test_client()
    response = client.get("/recommend/u1")
    assert response.status_code == 200
    data = response.get_json()
    assert "recommendations" in data
    assert "user_id" in data
