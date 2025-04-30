import os
import json
import pandas as pd
import numpy as np
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import json_util
from collections import Counter
import time

# Import necessary libraries for your chosen recommendation algorithm (e.g., scikit-learn)

# Connect to MongoDB - Support both local and cloud deployment
# The environment variable will be set in the deployment environment
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/mydatabase")
# For local development, you can use: mongodb://localhost:27017/mydatabase
# For Docker or cloud deployment: mongodb://mongodb:27017/mydatabase (service name)

# Add retry logic for MongoDB connection
max_retries = 30
retry_interval = 2
client = None
db = None

for attempt in range(max_retries):
    try:
        print(f"Attempting to connect to MongoDB at {MONGO_URI} (attempt {attempt+1}/{max_retries})")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Force a connection to verify it works
        client.admin.command('ping')
db = client.get_database()
        print("Successfully connected to MongoDB")
        break
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"Failed to connect to MongoDB: {e}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
        else:
            print("Maximum retry attempts reached. Could not connect to MongoDB.")
            # Instead of failing hard, we'll allow the app to start but recommendations won't work

# Helper function to parse MongoDB BSON to JSON-serializable format
def parse_json(data):
    return json.loads(json_util.dumps(data))


class RecommendationEngine:
    def __init__(self):
        self.products_df = None
        self.users_df = None
        self.interactions_df = None
        self.load_data()

    def load_data(self):
        """Load data from MongoDB into pandas DataFrames"""
        if db is None:
            print("Database connection not available. Using empty DataFrames.")
            self.products_df = pd.DataFrame()
            self.users_df = pd.DataFrame()
            self.interactions_df = pd.DataFrame()
            return
        
        try:
        # Load products
        products = list(db.products.find())
            self.products_df = pd.DataFrame(products) if products else pd.DataFrame()

        # Load users
        users = list(db.users.find())
            self.users_df = pd.DataFrame(users) if users else pd.DataFrame()

        # Load interactions
        interactions = list(db.interactions.find())
            self.interactions_df = pd.DataFrame(interactions) if interactions else pd.DataFrame()

        print(
            f"Loaded {len(self.products_df)} products, {len(self.users_df)} users, {len(self.interactions_df)} interactions"
        )
        except Exception as e:
            print(f"Error loading data from MongoDB: {e}")
            self.products_df = pd.DataFrame()
            self.users_df = pd.DataFrame()
            self.interactions_df = pd.DataFrame()

    def get_user_preferences(self, user_id):
        """Get a user's preferences"""
        user = self.users_df[self.users_df["_id"] == user_id]
        if user.empty:
            return None
        return user.iloc[0].get("preferences", [])

    def get_user_interactions(self, user_id):
        """Get products a user has interacted with"""
        if self.interactions_df is None or self.interactions_df.empty:
            return []

        user_interactions = self.interactions_df[
            self.interactions_df["user_id"] == user_id
        ]
        return user_interactions["product_id"].tolist()

    def get_category_products(self, categories, exclude_product_ids=None):
        """Get products from specific categories, excluding any in the exclude list"""
        if exclude_product_ids is None:
            exclude_product_ids = []

        if self.products_df is None or self.products_df.empty:
            return []

        # Filter by category and exclude already interacted products
        filtered_df = self.products_df[
            (self.products_df["category"].isin(categories))
            & (~self.products_df["_id"].isin(exclude_product_ids))
        ]

        # Sort by rating if available, otherwise by price (descending)
        if "rating" in filtered_df.columns:
            filtered_df = filtered_df.sort_values("rating", ascending=False)

        return filtered_df.to_dict("records")

    def get_similar_users(self, user_id, n=2):
        """Find similar users based on preferences and interactions"""
        if self.users_df is None or self.users_df.empty:
            return []

        # Get user preferences
        target_user_prefs = self.get_user_preferences(user_id)
        if not target_user_prefs:
            return []

        # Get user interactions
        target_user_interactions = set(self.get_user_interactions(user_id))

        # Calculate similarity for each user
        similar_users = []
        for idx, user in self.users_df.iterrows():
            if user["_id"] == user_id:
                continue

            # Calculate preference similarity
            user_prefs = user.get("preferences", [])
            pref_overlap = len(set(target_user_prefs) & set(user_prefs))

            # Get this user's interactions
            user_interactions = set(self.get_user_interactions(user["_id"]))

            # Calculate interaction similarity
            interaction_overlap = len(target_user_interactions & user_interactions)

            # Combined similarity score (more weight on interactions)
            similarity = (pref_overlap * 0.4) + (interaction_overlap * 0.6)

            similar_users.append({"user_id": user["_id"], "similarity": similarity})

        # Sort by similarity and get top N
        similar_users.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_users[:n]

    def get_recommended_products(self, user_id, n_recommendations=5):
        """Get product recommendations for a user"""
        # Already interacted products - exclude from new recommendations
        interacted_product_ids = self.get_user_interactions(user_id)

        # Get user's preferred categories
        preferred_categories = self.get_user_preferences(user_id)

        # Recommendation strategy 1: Get products from user's preferred categories
        category_recommendations = []
        if preferred_categories:
            category_recommendations = self.get_category_products(
                preferred_categories, interacted_product_ids
            )

        # Recommendation strategy 2: Get products that similar users have interacted with
        similar_user_recommendations = []
        similar_users = self.get_similar_users(user_id)

        # Get all product IDs interacted with by similar users
        similar_users_product_ids = []
        for similar_user in similar_users:
            similar_user_id = similar_user["user_id"]
            product_ids = self.get_user_interactions(similar_user_id)
            similar_users_product_ids.extend(product_ids)

        # Count frequency of each product ID
        product_id_counts = Counter(similar_users_product_ids)

        # Get the most common products that current user hasn't interacted with
        most_common_products = [
            product_id
            for product_id, count in product_id_counts.most_common()
            if product_id not in interacted_product_ids
        ]

        # Get full product details
        if most_common_products:
            similar_user_recommendations = [
                product
                for product in self.products_df.to_dict("records")
                if product["_id"] in most_common_products
            ]

        # Combine recommendations, prioritizing similar user recommendations
        combined_recommendations = []

        # Add similar users recommendations first (more personalized)
        combined_recommendations.extend(similar_user_recommendations)

        # Add category recommendations next
        remaining_slots = n_recommendations - len(combined_recommendations)
        if remaining_slots > 0 and category_recommendations:
            # Add only the products not already in combined_recommendations
            added = 0
            for product in category_recommendations:
                if added >= remaining_slots:
                    break
                # Check if product is already in combined_recommendations
                if not any(
                    r["_id"] == product["_id"] for r in combined_recommendations
                ):
                    combined_recommendations.append(product)
                    added += 1

        # If still not enough, add popular products (mix rating and random)
        remaining_slots = n_recommendations - len(combined_recommendations)
        if remaining_slots > 0:
            if "rating" in self.products_df.columns:
                popular_df = self.products_df.copy()

                # Mix top-rated + random shuffle 
                popular_df = popular_df.sort_values("rating", ascending=False)


                cutoff = int(len(popular_df) * 0.8)
                candidate_products = popular_df.iloc[:cutoff].sample(frac=1).to_dict("records")
            else:
                candidate_products = self.products_df.sample(frac=1).to_dict("records")

            added = 0
            for product in candidate_products:
                if added >= remaining_slots:
                    break
                if (
                    not any(r["_id"] == product["_id"] for r in combined_recommendations)
                    and product["_id"] not in interacted_product_ids
                ):
                    combined_recommendations.append(product)
                    added += 1

        return combined_recommendations[:n_recommendations]


# Instantiate the recommendation engine
recommendation_engine = RecommendationEngine()


def get_recommendations(user_id: str, n_recommendations: int = 5):
    """Get recommendations for a user"""
    print(f"Generating recommendations for user: {user_id}")

    try:
        # Get recommendations using the engine
        recommendations = recommendation_engine.get_recommended_products(
            user_id, n_recommendations
        )

        if not recommendations:
            print(
                f"No recommendations found for user {user_id}. Returning popular items."
            )
            # Return popular items or other fallback recommendations
            popular_products = list(
                db.products.find().sort("rating", -1).limit(n_recommendations)
            )
            return parse_json(popular_products)

        print(f"Generated {len(recommendations)} recommendations for user {user_id}")

        # Convert to JSON-serializable format
        return parse_json(recommendations)

    except Exception as e:
        print(f"Error generating recommendations for user {user_id}: {e}")
        # Fallback: return popular items
        try:
            popular_products = list(
                db.products.find().sort("rating", -1).limit(n_recommendations)
            )
            return parse_json(popular_products)
        except Exception as db_e:
            print(f"Error fetching popular products: {db_e}")
            return []  # Return empty list if DB fails


# Example usage (optional, for testing)
if __name__ == "__main__":
    for user_id in ["user1", "user2", "user3", "user4", "user5"]:
        recs = get_recommendations(user_id)
        print(f"\nRecommendations for {user_id}:")
        for rec in recs:
            print(f"- {rec['name']} ({rec['category']}) - ${rec['price']}")
