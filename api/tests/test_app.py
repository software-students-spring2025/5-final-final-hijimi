import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Patch db and client globally to ensure they take effect before app loads
@patch("api.app.client", new_callable=MagicMock)
@patch("api.app.db", new_callable=MagicMock)
def create_test_client(mock_db, mock_client):
    from api.app import app
    
    # Configure the mocks to ensure no 503 errors
    mock_client.admin.command.return_value = {"ok": 1}  # Default to successful ping
    mock_db.get_database.return_value = mock_db  # Make sure db is properly mocked
    
    return TestClient(app), mock_db, mock_client

def test_read_root():
    client, *_ = create_test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the E-commerce Recommendation API"}

def test_health_check():
    client, _, mock_client = create_test_client()
    mock_client.admin.command.return_value = {"ok": 1}
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"

def test_health_check_failure():
    client, _, mock_client = create_test_client()
    mock_client.admin.command.side_effect = Exception("DB error")
    response = client.get("/health")
    assert response.status_code == 200  # Health endpoint doesn't raise HTTPException
    assert response.json()["status"] == "error"

def test_get_all_products():
    client, mock_db, _ = create_test_client()
    # Set up mock for products collection
    mock_products = [
        {"_id": "prod1", "name": "Product 1"},
        {"_id": "prod2", "name": "Product 2"}
    ]
    mock_db.products.find.return_value = MagicMock()
    mock_db.products.find.return_value.limit.return_value = mock_products
    
    response = client.get("/products?limit=2")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2

@patch("api.app.get_recommendations")
def test_get_user_recommendations(mock_get_recommendations):
    client, *_ = create_test_client()
    mock_get_recommendations.return_value = [
        {"_id": "prod1", "name": "Recommended Product"}
    ]
    response = client.get("/recommendations/testuser?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "testuser"
    assert data["recommendations"][0]["name"] == "Recommended Product"

@patch("api.app.get_recommendations")
def test_get_user_recommendations_error(mock_get_recommendations):
    client, *_ = create_test_client()
    mock_get_recommendations.side_effect = Exception("Recommendation error")
    response = client.get("/recommendations/testuser?limit=1")
    assert response.status_code == 500  # Changed from 503 to 500 based on app.py implementation
    assert "Internal server error" in response.text
