import os
import json
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bson import json_util
from collections import Counter

# Import necessary libraries for your chosen recommendation algorithm (e.g., scikit-learn)

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydatabase")
client = MongoClient(MONGO_URI)
db = client.get_database()


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
        # Load products
        products = list(db.products.find())
        self.products_df = pd.DataFrame(products)

        # Load users
        users = list(db.users.find())
        self.users_df = pd.DataFrame(users)

        # Load interactions
        interactions = list(db.interactions.find())
        self.interactions_df = pd.DataFrame(interactions)

        print(
            f"Loaded {len(self.products_df)} products, {len(self.users_df)} users, {len(self.interactions_df)} interactions"
        )

    def get_user_preferences(self, user_id):
        """Get a user's preferences"""
        user = self.users_df[self.users_df["_id"] == user_id]
        if user.empty:
            return []
        return user.iloc[0].get("preferences", [])

    def get_user_interactions(self, user_id):
        """Get products a user has interacted with"""
        if self.interactions_df is None or self.interactions_df.empty:
            return []

        user_interactions = self.interactions_df[
            self.interactions_df["user_id"] == user_id
        ]
        return user_interactions["product_id"].tolist()

    def get_category_products(self, categories, exclude_product_ids=None, brand=None):
        """Get products from specific categories, excluding any in the exclude list
        
        Args:
            categories (list): List of categories to match products against
            exclude_product_ids (list, optional): List of product IDs to exclude. Defaults to None.
            brand (str, optional): Filter by brand name. Defaults to None.
            
        Returns:
            list: List of matching product dictionaries sorted by rating
        """
        if exclude_product_ids is None:
            exclude_product_ids = []

        if self.products_df is None or self.products_df.empty:
            return []

        # Create a filter for products that have any of the requested categories
        # Check if the product's categories list contains any of the requested categories
        # This handles the new schema where categories is a list instead of a single value
        filtered_products = []
        
        for _, product in self.products_df.iterrows():
            # Skip products that are in the exclude list
            if product["_id"] in exclude_product_ids:
                continue
                
            # Skip products that don't match the brand filter (if provided)
            if brand and product.get("brand") != brand:
                continue
                
            # Check if any of the requested categories are in the product's categories
            if "categories" in product:
                product_categories = product["categories"]
                # If any requested category matches any product category, include this product
                if any(category in product_categories for category in categories):
                    filtered_products.append(product.to_dict())
            # Fallback for old schema with single "category" field
            elif "category" in product and product["category"] in categories:
                filtered_products.append(product.to_dict())
                
        # Sort by rating (descending)
        filtered_products.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
        return filtered_products

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

    def get_recommended_products(self, user_id, n_recommendations=5, brand_filter=None):
        """Get product recommendations for a user with optional brand filtering"""
        # Already interacted products - exclude from new recommendations
        interacted_product_ids = self.get_user_interactions(user_id)

        # Get user's preferred categories
        preferred_categories = self.get_user_preferences(user_id)

        # Recommendation strategy 1: Get products from user's preferred categories
        category_recommendations = []
        if preferred_categories:
            category_recommendations = self.get_category_products(
                preferred_categories, interacted_product_ids, brand_filter
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

        # Get full product details for the most common products with brand filtering if needed
        if most_common_products:
            for product in self.products_df.to_dict("records"):
                if product["_id"] in most_common_products:
                    # Apply brand filter if specified
                    if brand_filter and product.get("brand") != brand_filter:
                        continue
                    similar_user_recommendations.append(product)

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

        # If still not enough, add popular products (highest rated)
        remaining_slots = n_recommendations - len(combined_recommendations)
        if remaining_slots > 0:
            # Sort by rating if available, but also apply brand filter if needed
            filtered_products = []
            for product in self.products_df.to_dict("records"):
                # Apply brand filter if specified
                if brand_filter and product.get("brand") != brand_filter:
                    continue
                filtered_products.append(product)
            
            # Sort the filtered products by rating
            popular_products = sorted(
                filtered_products, 
                key=lambda x: x.get("rating", 0), 
                reverse=True
            )

            # Add only the products not already in combined_recommendations
            added = 0
            for product in popular_products:
                if added >= remaining_slots:
                    break
                # Check if product is already in combined_recommendations and not interacted with
                if (
                    not any(
                        r["_id"] == product["_id"] for r in combined_recommendations
                    )
                    and product["_id"] not in interacted_product_ids
                ):
                    combined_recommendations.append(product)
                    added += 1

        return combined_recommendations[:n_recommendations]
        
    def search_products(self, query_terms, brand=None, sort_by="rating", limit=20):
        """
        Search for products matching the query terms across multiple fields.
        
        Args:
            query_terms (list): List of search terms to match against product data
            brand (str, optional): Filter by brand name. Defaults to None.
            sort_by (str, optional): Field to sort results by. Defaults to "rating".
            limit (int, optional): Maximum number of results to return. Defaults to 20.
            
        Returns:
            list: List of matching product dictionaries
        """
        if not query_terms or not self.products_df.any().any():
            return []
        
        # Convert all terms to lowercase for case-insensitive matching
        query_terms = [term.lower() for term in query_terms]
        
        # Score each product based on how well it matches the query terms
        scored_products = []
        
        for _, product in self.products_df.iterrows():
            # Skip products that don't match the brand filter (if provided)
            if brand and product.get("brand") != brand:
                continue
                
            score = 0
            product_dict = product.to_dict()
            
            # Check product name (highest weight)
            if "name" in product_dict:
                name = product_dict["name"].lower()
                for term in query_terms:
                    if term in name:
                        score += 10  # Higher weight for name matches
            
            # Check product description
            if "description" in product_dict:
                description = product_dict["description"].lower()
                for term in query_terms:
                    if term in description:
                        score += 5  # Medium weight for description matches
            
            # Check product categories
            if "categories" in product_dict and isinstance(product_dict["categories"], list):
                categories = [cat.lower() for cat in product_dict["categories"]]
                for term in query_terms:
                    if any(term in category for category in categories):
                        score += 8  # High weight for category matches
            # Fallback for old schema with single category
            elif "category" in product_dict:
                category = product_dict["category"].lower()
                for term in query_terms:
                    if term in category:
                        score += 8
            
            # Check product brand
            if "brand" in product_dict:
                prod_brand = product_dict["brand"].lower()
                for term in query_terms:
                    if term in prod_brand:
                        score += 7  # Medium-high weight for brand matches
            
            # Check product attributes
            if "attributes" in product_dict and isinstance(product_dict["attributes"], dict):
                for attr_key, attr_value in product_dict["attributes"].items():
                    attr_str = f"{attr_key} {attr_value}".lower()
                    for term in query_terms:
                        if term in attr_str:
                            score += 3  # Lower weight for attribute matches
            
            # Only include products with a positive score
            if score > 0:
                # Add the score to the product dictionary
                product_dict["search_score"] = score
                scored_products.append(product_dict)
        
        # First sort by search relevance score (descending)
        scored_products.sort(key=lambda x: x.get("search_score", 0), reverse=True)
        
        # Then, if products have the same search score, sort by the specified sort field
        if sort_by and sort_by != "search_score":
            # Get the top matches by search score
            top_matches = scored_products[:limit*2]  # Get more than needed for secondary sorting
            
            # Group by search score
            score_groups = {}
            for product in top_matches:
                score = product.get("search_score", 0)
                if score not in score_groups:
                    score_groups[score] = []
                score_groups[score].append(product)
            
            # Sort each group by the secondary sort criteria
            for score, products in score_groups.items():
                # For rating, price, etc., use numeric sorting
                reverse_sort = sort_by == "rating"  # Higher ratings first
                products.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse_sort)
            
            # Rebuild the sorted list
            sorted_products = []
            for score in sorted(score_groups.keys(), reverse=True):
                sorted_products.extend(score_groups[score])
            
            scored_products = sorted_products
        
        # Return the top results up to the limit
        return scored_products[:limit]

    def get_available_brands(self):
        """Get a list of all unique brands in the products database"""
        if self.products_df is None or self.products_df.empty:
            return []
            
        if "brand" not in self.products_df.columns:
            return []
            
        # Extract unique brands and sort alphabetically
        brands = sorted(self.products_df["brand"].unique().tolist())
        return brands
        
    def get_available_categories(self):
        """Get a list of all unique categories in the products database"""
        if self.products_df is None or self.products_df.empty:
            return []
            
        # Handle both new schema (categories array) and old schema (category field)
        categories = set()
        
        if "categories" in self.products_df.columns:
            # Extract all categories from the categories arrays
            for cats in self.products_df["categories"].dropna():
                if isinstance(cats, list):
                    categories.update(cats)
        
        if "category" in self.products_df.columns:
            # Add categories from the old schema
            categories.update(self.products_df["category"].dropna().unique())
            
        # Sort alphabetically
        return sorted(list(categories))


# Instantiate the recommendation engine
recommendation_engine = RecommendationEngine()


def get_recommendations(user_id: str, n_recommendations: int = 5, brand: str = None):
    """Get recommendations for a user with optional brand filtering"""
    print(f"Generating recommendations for user: {user_id}")

    try:
        # Get recommendations using the engine
        recommendations = recommendation_engine.get_recommended_products(
            user_id, n_recommendations, brand_filter=brand
        )

        if not recommendations:
            print(
                f"No recommendations found for user {user_id}. Returning popular items."
            )
            # Return popular items or other fallback recommendations
            query = {"rating": {"$exists": True}}
            if brand:
                query["brand"] = brand
                
            popular_products = list(
                db.products.find(query).sort("rating", -1).limit(n_recommendations)
            )
            return parse_json(popular_products)

        print(f"Generated {len(recommendations)} recommendations for user {user_id}")

        # Convert to JSON-serializable format
        return parse_json(recommendations)

    except Exception as e:
        print(f"Error generating recommendations for user {user_id}: {e}")
        # Fallback: return popular items
        try:
            query = {"rating": {"$exists": True}}
            if brand:
                query["brand"] = brand
                
            popular_products = list(
                db.products.find(query).sort("rating", -1).limit(n_recommendations)
            )
            return parse_json(popular_products)
        except Exception as db_e:
            print(f"Error fetching popular products: {db_e}")
            return []  # Return empty list if DB fails


def search_products(query: str, brand: str = None, sort_by: str = "rating", limit: int = 20):
    """Search for products matching the query terms"""
    print(f"Searching products with query: {query}")
    
    try:
        # Split the query into terms
        query_terms = query.split()
        
        # Use the search function from the recommendation engine
        search_results = recommendation_engine.search_products(
            query_terms, brand=brand, sort_by=sort_by, limit=limit
        )
        
        if not search_results:
            print(f"No products found matching query: {query}")
            return []
            
        print(f"Found {len(search_results)} products matching query: {query}")
        
        # Convert to JSON-serializable format
        return parse_json(search_results)
        
    except Exception as e:
        print(f"Error searching products with query {query}: {e}")
        return []


def get_available_brands():
    """Get a list of all unique brands in the products database"""
    try:
        return recommendation_engine.get_available_brands()
    except Exception as e:
        print(f"Error getting available brands: {e}")
        return []
        
        
def get_available_categories():
    """Get a list of all unique categories in the products database"""
    try:
        return recommendation_engine.get_available_categories()
    except Exception as e:
        print(f"Error getting available categories: {e}")
        return []


# Example usage (optional, for testing)
if __name__ == "__main__":
    for user_id in ["user1", "user2", "user3"]:
        recs = get_recommendations(user_id)
        print(f"\nRecommendations for {user_id}:")
        for i, rec in enumerate(recs[:3], 1):  # Show only top 3 for brevity
            print(f"{i}. {rec['name']} ({'/'.join(rec['categories'])}) - ${rec['price']}")
    
    # Test search functionality
    print("\nSearch results for 'desk':")
    results = search_products("desk")
    for i, result in enumerate(results[:3], 1):  # Show only top 3 for brevity
        print(f"{i}. {result['name']} ({result['brand']}) - Score: {result.get('search_score', 0)}")
    
    # Test brand and category listing
    print("\nAvailable brands:")
    brands = get_available_brands()
    print(", ".join(brands[:10]))  # Show first 10 brands
    
    print("\nAvailable categories:")
    categories = get_available_categories()
    print(", ".join(categories[:10]))  # Show first 10 categories
