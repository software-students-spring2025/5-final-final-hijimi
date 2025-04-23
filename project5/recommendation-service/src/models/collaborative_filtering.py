# recommendation-service/src/models/collaborative_filtering.py
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class CollaborativeFilteringModel:
    def __init__(self, db):
        self.db = db
        self.user_item_matrix = None
        self.item_similarity_matrix = None
        self.trained = False

    def train(self):
        """Train the collaborative filtering model"""
        # Get interactions from MongoDB
        interactions = list(self.db.interactions.find())
        
        # Convert to DataFrame
        df = pd.DataFrame(interactions)
        
        # Create user-item matrix
        self.user_item_matrix = df.pivot_table(
            index='userId', 
            columns='productId', 
            values='rating'
        ).fillna(0)
        
        # Calculate item-item similarity matrix
        self.item_similarity_matrix = cosine_similarity(self.user_item_matrix.T)
        
        # Create mapping of product IDs to matrix indices
        self.product_indices = {
            product_id: i for i, product_id in 
            enumerate(self.user_item_matrix.columns)
        }
        
        self.trained = True
        return self

    def recommend_for_user(self, user_id, limit=10):
        """Generate recommendations for a user"""
        if not self.trained:
            self.train()
            
        # Check if user exists in the matrix
        if user_id not in self.user_item_matrix.index:
            # Return popular items if user not found
            return self._get_popular_items(limit)
        
        # Get user's ratings
        user_ratings = self.user_item_matrix.loc[user_id]
        
        # Calculate predicted ratings
        predicted_ratings = np.dot(self.item_similarity_matrix, user_ratings)
        
        # Get indices of already rated items
        rated_indices = user_ratings.nonzero()[0]
        
        # Set rated items to -1 to exclude them from recommendations
        predicted_ratings[rated_indices] = -1
        
        # Get top N recommendations
        rec_indices = predicted_ratings.argsort()[-limit:][::-1]
        
        # Map indices back to product IDs
        reverse_mapping = {v: k for k, v in self.product_indices.items()}
        recommendations = [
            {
                "product_id": reverse_mapping[idx],
                "score": float(predicted_ratings[idx])
            }
            for idx in rec_indices
        ]
        
        return recommendations

    def find_similar(self, product_id, limit=10):
        """Find similar products"""
        if not self.trained:
            self.train()
            
        # Check if product exists
        if product_id not in self.product_indices:
            return []
            
        # Get product index
        idx = self.product_indices[product_id]
        
        # Get similarity scores
        similarity_scores = self.item_similarity_matrix[idx]
        
        # Sort indices by similarity scores
        similar_indices = similarity_scores.argsort()[-limit-1:][::-1]
        
        # Exclude the product itself
        similar_indices = similar_indices[similar_indices != idx][:limit]
        
        # Map indices back to product IDs
        reverse_mapping = {v: k for k, v in self.product_indices.items()}
        similar_products = [
            {
                "product_id": reverse_mapping[idx],
                "similarity": float(similarity_scores[idx])
            }
            for idx in similar_indices
        ]
        
        return similar_products
        
    def _get_popular_items(self, limit=10):
        """Get popular items based on interaction count"""
        # Aggregate to find most popular products
        pipeline = [
            {"$group": {"_id": "$productId", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        popular_products = list(self.db.interactions.aggregate(pipeline))
        
        return [
            {
                "product_id": item["_id"],
                "score": item["count"]
            }
            for item in popular_products
        ]