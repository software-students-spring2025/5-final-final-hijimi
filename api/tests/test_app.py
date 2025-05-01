import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# More comprehensive mocking of MongoDB
@patch("api.app.client", autospec=True)
@patch("api.app.db", autospec=True)
def create_test_client(mock_db, mock_client):
    # Import app after patching
    from api.app import app
    
    # Set up admin mock for ping tests
    mock_admin = MagicMock()
    mock_admin.command.return_value = {"ok": 1}
    mock_client.admin = mock_admin
    
    # Set up collections
    mock_db.products = MagicMock()
    
    # Ensure db.get_database() returns itself
    mock_db.get_database.return_value = mock_db
    
    return TestClient(app), mock_db, mock_client

def test_read_root():
    client, *_ = create_test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the E-commerce Recommendation API"}

def test_health_check():
    client, _, mock_client = create_test_client()
    # 确保admin.command返回成功
    mock_client.admin.command.return_value = {"ok": 1}
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"

def test_health_check_failure():
    client, _, mock_client = create_test_client()
    # 模拟连接失败
    mock_client.admin.command.side_effect = Exception("DB error")
    
    response = client.get("/health")
    assert response.status_code == 200  # 健康检查endpoint总是返回200
    assert response.json()["status"] == "error"

def test_get_all_products():
    client, mock_db, _ = create_test_client()
    
    # 设置products测试数据
    mock_products = [
        {"_id": "prod1", "name": "Product 1"},
        {"_id": "prod2", "name": "Product 2"}
    ]
    
    # 更完整的mock链
    mock_find = MagicMock()
    mock_find.limit.return_value = mock_products
    mock_db.products.find.return_value = mock_find
    
    response = client.get("/products?limit=2")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2

@patch("api.app.get_recommendations")
def test_get_user_recommendations(mock_get_recommendations):
    client, *_ = create_test_client()
    
    # 设置推荐测试数据
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
    
    # 模拟推荐引擎错误
    mock_get_recommendations.side_effect = Exception("Recommendation error")
    
    response = client.get("/recommendations/testuser?limit=1")
    assert response.status_code == 500  # app.py中应该是捕获异常并返回500
    assert "Internal server error" in response.text
