import pytest
from unittest.mock import patch, MagicMock
import recommender.recommender as recommender_module

@pytest.fixture
def mock_db():
    with patch.object(recommender_module, 'db') as mock_db:
        yield mock_db

@pytest.fixture
def engine(mock_db):
    # Mock MongoDB collections
    mock_db.products.find.return_value = [
        {"_id": "p1", "name": "Phone", "category": "Electronics", "rating": 4.5, "price": 500},
        {"_id": "p2", "name": "Book", "category": "Books", "rating": 4.8, "price": 20},
        {"_id": "p3", "name": "Headphones", "category": "Electronics", "rating": 4.2, "price": 150},
    ]
    mock_db.users.find.return_value = [
        {"_id": "user1", "preferences": ["Electronics", "Books"]},
        {"_id": "user2", "preferences": ["Books"]},
    ]
    mock_db.interactions.find.return_value = [
        {"user_id": "user1", "product_id": "p1"},
        {"user_id": "user2", "product_id": "p2"},
    ]
    return recommender_module.RecommendationEngine()

def test_load_data(engine):
    assert len(engine.products_df) == 3
    assert len(engine.users_df) == 2
    assert len(engine.interactions_df) == 2

def test_get_user_preferences(engine):
    assert engine.get_user_preferences("user1") == ["Electronics", "Books"]
    assert engine.get_user_preferences("nonexistent") is None

def test_get_user_interactions(engine):
    assert "p1" in engine.get_user_interactions("user1")
    assert engine.get_user_interactions("nonexistent") == []

def test_get_category_products(engine):
    products = engine.get_category_products(["Electronics"])
    assert all(p["category"] == "Electronics" for p in products)

def test_get_similar_users(engine):
    similar_users = engine.get_similar_users("user1")
    assert isinstance(similar_users, list)
    assert all("user_id" in user for user in similar_users)

def test_get_recommended_products_normal(engine):
    recs = engine.get_recommended_products("user1", n_recommendations=3)
    assert isinstance(recs, list)
    assert len(recs) <= 3

def test_get_recommended_products_no_preferences(engine):
    # Mock users with empty preferences
    engine.users_df = engine.users_df.copy()
    engine.users_df.loc[engine.users_df["_id"] == "user1", "preferences"] = [[]]
    recs = engine.get_recommended_products("user1", n_recommendations=3)
    assert isinstance(recs, list)

def test_get_recommended_products_no_interactions(engine):
    # Mock interactions as empty
    engine.interactions_df = engine.interactions_df.iloc[0:0]
    recs = engine.get_recommended_products("user1", n_recommendations=3)
    assert isinstance(recs, list)

def test_get_recommendations_success(mock_db):
    mock_db.products.find.return_value.sort.return_value.limit.return_value = [
        {"_id": "p4", "name": "Popular Product", "category": "Fashion", "rating": 4.9, "price": 100}
    ]
    recs = recommender_module.get_recommendations("user1", n_recommendations=5)
    assert isinstance(recs, list)

def test_get_recommendations_fallback(mock_db):
    # Simulate error during recommendation
    with patch.object(recommender_module.recommendation_engine, 'get_recommended_products', side_effect=Exception("simulate error")):
        mock_db.products.find.return_value.sort.return_value.limit.return_value = [
            {"_id": "p5", "name": "Fallback Product", "category": "Toys", "rating": 4.5, "price": 30}
        ]
        recs = recommender_module.get_recommendations("user1", n_recommendations=5)
        assert isinstance(recs, list)

def test_parse_json():
    data = {"key": "value"}
    parsed = recommender_module.parse_json(data)
    assert isinstance(parsed, dict)
