import os
from pymongo import MongoClient
import pandas as pd
# Import necessary libraries for your chosen recommendation algorithm (e.g., scikit-learn)

# Connect to MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/mydatabase')
client = MongoClient(MONGO_URI)
db = client.get_database()

# --- Placeholder for Recommendation Logic --- 
# This is where you'll implement your recommendation algorithm.
# For example, load a pre-trained model or calculate recommendations based on user data.

def get_recommendations(user_id: str, n_recommendations: int = 5):
    """Generates product recommendations for a given user."""
    print(f"Generating recommendations for user: {user_id}")
    
    # Example: Fetch user interactions
    try:
        interactions = list(db.interactions.find({'user_id': user_id}))
        if not interactions:
            print(f"No interaction data found for user {user_id}. Returning generic recommendations.")
            # Return popular items or other fallback recommendations
            popular_products = list(db.products.find().limit(n_recommendations))
            return popular_products 

        # --- Add your recommendation algorithm here --- 
        # Based on interactions, calculate or retrieve recommendations.
        # This is a very basic placeholder: recommending products the user interacted with.
        product_ids = [i['product_id'] for i in interactions]
        recommendations = list(db.products.find({'_id': {'$in': product_ids}}).limit(n_recommendations))
        
        # If fewer recommendations found than requested, add popular items
        if len(recommendations) < n_recommendations:
             popular_products = list(db.products.find({'_id': {'$nin': product_ids}}).limit(n_recommendations - len(recommendations)))
             recommendations.extend(popular_products)

        print(f"Generated {len(recommendations)} recommendations for user {user_id}")
        return recommendations

    except Exception as e:
        print(f"Error generating recommendations for user {user_id}: {e}")
        # Fallback: return popular items
        try:
            popular_products = list(db.products.find().limit(n_recommendations))
            return popular_products
        except Exception as db_e:
            print(f"Error fetching popular products: {db_e}")
            return [] # Return empty list if DB fails

# Example usage (optional, for testing)
if __name__ == '__main__':
    test_user = 'user1'
    recs = get_recommendations(test_user)
    print(f"\nRecommendations for {test_user}:")
    for rec in recs:
        print(f"- {rec['name']} ({rec['category']})")

    test_user_no_data = 'user_new'
    recs_new = get_recommendations(test_user_no_data)
    print(f"\nRecommendations for {test_user_no_data}:")
    for rec in recs_new:
        print(f"- {rec['name']} ({rec['category']})") 