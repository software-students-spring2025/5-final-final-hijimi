import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Patch MongoDB initialization before importing the app
with patch('pymongo.MongoClient', autospec=False) as mock_mongo_client:
    # Setup mock MongoDB client
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_mongo_client.return_value = mock_client
    mock_client.get_database.return_value = mock_db
    mock_client.admin.command.return_value = {"ok": 1}

    # Now import app after patching
    from api.app import app
    
    # Create test client
    client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the E-commerce Recommendation API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"

def test_health_check_failure():
    # Temporarily change the mock behavior
    original_command = mock_client.admin.command
    mock_client.admin.command.side_effect = Exception("DB error")
    
    response = client.get("/health")
    assert response.status_code == 200  # Health check endpoint always returns 200
    assert response.json()["status"] == "error"
    
    # Restore the original mock
    mock_client.admin.command = original_command

def test_get_all_products():
    # Set up products test data
    mock_products = [
        {"_id": "prod1", "name": "Product 1"},
        {"_id": "prod2", "name": "Product 2"}
    ]
    
    # Set up cursor mock
    mock_cursor = MagicMock()
    mock_cursor.return_value = mock_products
    mock_db.products.find.return_value = mock_products
    
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2

@patch("api.app.get_recommendations")
def test_get_user_recommendations(mock_get_recommendations):
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
    # Simulate recommendation engine error
    mock_get_recommendations.side_effect = Exception("Recommendation error")
    
    response = client.get("/recommendations/testuser?limit=1")
    assert response.status_code == 500  # app.py should catch exceptions and return 500
    assert "Internal server error" in response.text
