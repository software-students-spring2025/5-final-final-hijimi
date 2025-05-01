import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Using regular patch instead of autospec to avoid connection attempts
@patch("api.app.client")
@patch("api.app.db")
def create_test_client(mock_db, mock_client):
    # Import app after patching
    from api.app import app
    
    # Set up admin mock for ping tests
    mock_admin = MagicMock()
    mock_admin.command.return_value = {"ok": 1}
    mock_client.admin = mock_admin
    
    # Set up collections
    mock_products = MagicMock()
    mock_db.products = mock_products
    
    # Ensure no real connections are attempted
    mock_client._topology = MagicMock()
    
    return TestClient(app), mock_db, mock_client

def test_read_root():
    client, *_ = create_test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the E-commerce Recommendation API"}

def test_health_check():
    client, _, mock_client = create_test_client()
    # Ensure admin.command returns success
    mock_client.admin.command.return_value = {"ok": 1}
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"

def test_health_check_failure():
    client, _, mock_client = create_test_client()
    # Simulate connection failure
    mock_client.admin.command.side_effect = Exception("DB error")
    
    response = client.get("/health")
    assert response.status_code == 200  # Health check endpoint always returns 200
    assert response.json()["status"] == "error"

def test_get_all_products():
    client, mock_db, _ = create_test_client()
    
    # Set up products test data
    mock_products = [
        {"_id": "prod1", "name": "Product 1"},
        {"_id": "prod2", "name": "Product 2"}
    ]
    
    # More complete mock chain
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = mock_products
    mock_db.products.find.return_value = mock_cursor
    
    response = client.get("/products?limit=2")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2

@patch("api.app.get_recommendations")
def test_get_user_recommendations(mock_get_recommendations):
    client, *_ = create_test_client()
    
    # Set up recommendation test data
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
    
    # Simulate recommendation engine error
    mock_get_recommendations.side_effect = Exception("Recommendation error")
    
    response = client.get("/recommendations/testuser?limit=1")
    assert response.status_code == 500  # app.py should catch exceptions and return 500
    assert "Internal server error" in response.text
