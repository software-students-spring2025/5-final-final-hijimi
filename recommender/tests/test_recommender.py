import pytest
import pandas as pd
from unittest.mock import patch
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from recommender import RecommendationEngine, parse_json

# Dummy data for mocking
dummy_products = [{"_id": "prod1", "name": "Product 1"}]
dummy_users = [{"_id": "user1", "preferences": ["electronics", "books"]}]
dummy_interactions = [{"user_id": "user1", "product_id": "prod1", "action": "view"}]

def test_parse_json():
    data = {"key": "value"}
    bson_data = json.loads(json.dumps(data))  # simulate bson
    result = parse_json(bson_data)
    assert result == {"key": "value"}

@patch("recommender.db")
def test_load_data(mock_db):
    mock_db.products.find.return_value = dummy_products
    mock_db.users.find.return_value = dummy_users
    mock_db.interactions.find.return_value = dummy_interactions

    engine = RecommendationEngine()
    assert isinstance(engine.products_df, pd.DataFrame)
    assert isinstance(engine.users_df, pd.DataFrame)
    assert isinstance(engine.interactions_df, pd.DataFrame)

@patch("recommender.db")
def test_get_user_preferences_found(mock_db):
    mock_db.products.find.return_value = dummy_products
    mock_db.users.find.return_value = dummy_users
    mock_db.interactions.find.return_value = dummy_interactions

    engine = RecommendationEngine()
    prefs = engine.get_user_preferences("user1")
    assert prefs == ["electronics", "books"]

@patch("recommender.db")
def test_get_user_preferences_not_found(mock_db):
    mock_db.products.find.return_value = dummy_products
    mock_db.users.find.return_value = dummy_users
    mock_db.interactions.find.return_value = dummy_interactions

    engine = RecommendationEngine()
    prefs = engine.get_user_preferences("nonexistent_user")
    assert prefs is None
