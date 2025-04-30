import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.app import app

client = TestClient(app)

# Test root endpoint
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the E-commerce Recommendation API"}

# Test health check - success
@patch("api.app.client")
def test_health_check(mock_client):
    mock_client.admin.command.return_value = {"ok": 1}
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# Test health check - failure
@patch("api.app.client")
def test_health_check_failure(mock_client):
    mock_client.admin.command.side_effect = Exception("DB error")
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "error"

# Test get all products
@patch("api.app.db")
def test_get_all_products(mock_db):
    mock_db.products.find.return_value.limit.return_value = [
        {"_id": "prod1", "name": "Product 1"},
        {"_id": "prod2", "name": "Product 2"},
    ]
    response = client.get("/products?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Product 1"

# Test recommendations with fallback
@patch("api.app.db")
@patch("api.app.get_recommendations")
def test_get_user_recommendations_with_fallback(mock_get_recommendations, mock_db):
    mock_get_recommendations.return_value = []
    mock_db.products.find.return_value.limit.return_value = [
        {"_id": "prod1", "name": "Fallback Product"}
    ]
    response = client.get("/recommendations/testuser?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "testuser"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["name"] == "Fallback Product"

# Test normal recommendations
@patch("api.app.get_recommendations")
def test_get_user_recommendations(mock_get_recommendations):
    mock_get_recommendations.return_value = [
        {"_id": "prod1", "name": "Recommended Product"}
    ]
    response = client.get("/recommendations/testuser?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "testuser"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["name"] == "Recommended Product"

# Test recommendation error
@patch("api.app.get_recommendations")
def test_get_user_recommendations_error(mock_get_recommendations):
    mock_get_recommendations.side_effect = Exception("Recommendation error")
    response = client.get("/recommendations/testuser?limit=1")
    assert response.status_code == 503  # match app.py error handling
    assert "Internal server error" in response.text
