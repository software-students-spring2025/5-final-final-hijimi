# recommendation-service/tests/test_collaborative_filtering.py
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from src.models.collaborative_filtering import CollaborativeFilteringModel

class TestCollaborativeFilteringModel:
    @pytest.fixture
    def mock_db(self):
        # Create a mock database with sample data
        mock_db = MagicMock()
        
        # Sample interactions
        interactions = [
            {"userId": "user1", "productId": "product1", "rating": 5},
            {"userId": "user1", "productId": "product2", "rating": 3},
            {"userId": "user1", "productId": "product3", "rating": 4},
            {"userId": "user2", "productId": "product1", "rating": 3},
            {"userId": "user2", "productId": "product3", "rating": 5},
            {"userId": "user3", "productId": "product2", "rating": 4},
            {"userId": "user3", "productId": "product3", "rating": 3},
        ]
        
        # Mock find method to return interactions
        mock_db.interactions.find = MagicMock(return_value=interactions)
        
        # Mock aggregate method to return popular products
        mock_db.interactions.aggregate = MagicMock(return_value=[
            {"_id": "product3", "count": 3},
            {"_id": "product1", "count": 2},
            {"_id": "product2", "count": 2},
        ])
        
        return mock_db
    
    def test_train(self, mock_db):
        # Instantiate the model with mock database
        model = CollaborativeFilteringModel(mock_db)
        
        # Train the model
        model.train()
        
        # Check if the user-item matrix is created correctly
        assert model.user_item_matrix is not None
        assert model.user_item_matrix.shape == (3, 3)  # 3 users, 3 products
        
        # Check if the item similarity matrix is created
        assert model.item_similarity_matrix is not None
        assert model.item_similarity_matrix.shape == (3, 3)  # 3x3 similarity matrix
        
        # Check if the model is marked as trained
        assert model.trained is True
    
    def test_recommend_for_user_existing(self, mock_db):
        # Instantiate and train the model
        model = CollaborativeFilteringModel(mock_db)
        model.train()
        
        # Get recommendations for an existing user
        recommendations = model.recommend_for_user("user1", limit=2)
        
        # Check recommendations
        assert len(recommendations) == 2
        assert "product_id" in recommendations[0]
        assert "score" in recommendations[0]
    
    def test_recommend_for_user_new(self, mock_db):
        # Instantiate and train the model
        model = CollaborativeFilteringModel(mock_db)
        model.train()
        
        # Get recommendations for a new user
        recommendations = model.recommend_for_user("new_user", limit=2)
        
        # Should return popular items
        assert len(recommendations) == 2
        assert recommendations[0]["product_id"] == "product3"
    
    def test_find_similar(self, mock_db):
        # Instantiate and train the model
        model = CollaborativeFilteringModel(mock_db)
        model.train()
        
        # Find similar products
        similar = model.find_similar("product1", limit=2)
        
        # Check similar products
        assert len(similar) == 2
        assert "product_id" in similar[0]
        assert "similarity" in similar[0]
    
    def test_find_similar_nonexistent(self, mock_db):
        # Instantiate and train the model
        model = CollaborativeFilteringModel(mock_db)
        model.train()
        
        # Find similar products for a nonexistent product
        similar = model.find_similar("nonexistent", limit=2)
        
        # Should return empty list
        assert similar == []