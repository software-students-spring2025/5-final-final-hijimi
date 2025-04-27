import os
import sys
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
# Add CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import json_util
import json

# Add the recommender directory to the Python path
# This allows importing the get_recommendations function
# Adjust the path ../ based on your final structure or consider packaging the recommender
sys.path.append(os.path.join(os.path.dirname(__file__), '../recommender'))
try:
    # Attempt to import the recommendation function
    from recommender import (
        get_recommendations, 
        search_products, 
        get_available_brands, 
        get_available_categories,
        parse_json
    )
except ImportError:
    # Provide a fallback if the recommender module isn't found or has issues
    print("Warning: Could not import get_recommendations from recommender module.")
    # Define parse_json if not imported from recommender
    def parse_json(data):
        return json.loads(json_util.dumps(data))

    def get_recommendations(user_id: str, n_recommendations: int = 5, brand: str = None):
        print("Fallback: Recommender not available.")
        # Simple fallback: return empty list or generic popular items from DB if accessible
        try:
             # Connect to MongoDB (consider centralizing connection logic)
             MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/mydatabase') # Use service name
             client = MongoClient(MONGO_URI)
             db = client.get_database()
             
             # Apply brand filter if specified
             query = {}
             if brand:
                 query["brand"] = brand
                 
             popular_products = list(db.products.find(query).sort("rating", -1).limit(n_recommendations))
             # Convert BSON ObjectId before returning from fallback
             return parse_json(popular_products) 
        except Exception as e:
             print(f"Fallback DB error: {e}")
             return []
             
    def search_products(query: str, brand: str = None, sort_by: str = "rating", limit: int = 20):
        print("Fallback: Search not available.")
        try:
            # Connect to MongoDB
            MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/mydatabase')
            client = MongoClient(MONGO_URI)
            db = client.get_database()
            
            # Build a basic search query using text search
            search_query = {"$text": {"$search": query}}
            if brand:
                search_query["brand"] = brand
                
            # Set up sorting
            sort_direction = -1 if sort_by == "rating" else 1
            
            # Execute the query
            search_results = list(
                db.products.find(search_query)
                .sort(sort_by, sort_direction)
                .limit(limit)
            )
            
            return parse_json(search_results)
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []
            
    def get_available_brands():
        print("Fallback: Get brands not available.")
        try:
            # Connect to MongoDB
            MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/mydatabase')
            client = MongoClient(MONGO_URI)
            db = client.get_database()
            
            # Get unique brands
            brands = db.products.distinct("brand")
            return sorted(brands)
        except Exception as e:
            print(f"Fallback get brands error: {e}")
            return []
            
    def get_available_categories():
        print("Fallback: Get categories not available.")
        try:
            # Connect to MongoDB
            MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/mydatabase')
            client = MongoClient(MONGO_URI)
            db = client.get_database()
            
            # Check if we have the new schema with categories array
            if db.products.find_one({"categories": {"$exists": True}}):
                # Get distinct categories from the arrays by using aggregation
                pipeline = [
                    {"$unwind": "$categories"},
                    {"$group": {"_id": "$categories"}},
                    {"$sort": {"_id": 1}}
                ]
                categories = [doc["_id"] for doc in db.products.aggregate(pipeline)]
                return categories
            else:
                # Fall back to the old schema with category field
                categories = db.products.distinct("category")
                return sorted(categories)
        except Exception as e:
            print(f"Fallback get categories error: {e}")
            return []

app = FastAPI(
    title="E-commerce Recommendation API",
    description="API for serving product recommendations and search results.",
    version="0.2.0"
)

# --- CORS Configuration ---
# Define allowed origins (where the frontend is running)
origins = [
    "http://localhost:8080", # Frontend origin when running locally
    "http://localhost:8081", # Frontend running on port 8081
    "http://localhost",      # Sometimes needed depending on browser/setup
    # Add the URL of your deployed frontend on Digital Ocean later
    # "https://your-deployed-frontend-url.com", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of origins allowed to make requests
    allow_credentials=True, # Allow cookies (if needed in the future)
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)
# --- End CORS Configuration ---

# Connect to MongoDB
# Use the service name 'mongodb' from docker-compose or Kubernetes
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/mydatabase')
client = MongoClient(MONGO_URI)
db = client.get_database()

@app.get("/")
def read_root():
    return {"message": "Welcome to the E-commerce Recommendation API", "version": "0.2.0"}

@app.get("/recommendations/{user_id}")
def get_user_recommendations(
    user_id: str, 
    limit: int = 5, 
    brand: Optional[str] = None
):
    """
    Endpoint to get product recommendations for a specific user.
    
    Args:
        user_id: The ID of the user to get recommendations for
        limit: Maximum number of recommendations to return (default: 5)
        brand: Optional brand filter
    """
    try:
        # Call the recommendation logic from the recommender module
        recommendations = get_recommendations(user_id, n_recommendations=limit, brand=brand)
        
        if not recommendations:
            # Handle case where no recommendations are generated (e.g., new user)
            # Return popular items as a fallback
             print(f"No specific recommendations for {user_id}, returning popular items.")
             query = {}
             if brand:
                 query["brand"] = brand
                 
             popular_products = list(db.products.find(query).sort("rating", -1).limit(limit))
             if not popular_products:
                  return {"user_id": user_id, "recommendations": [], "message": "No popular products found."}
             # Ensure fallback popular products are also parsed
             popular_products_json = parse_json(popular_products)
             return {"user_id": user_id, "recommendations": popular_products_json}

        # Return with user info
        return {"user_id": user_id, "recommendations": recommendations} 

    except Exception as e:
        print(f"Error in /recommendations/{user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/products")
def get_all_products(
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "rating",
    sort_order: str = "desc",
    brand: Optional[str] = None,
    category: Optional[str] = None
):
    """
    Endpoint to get a list of products with various filtering and sorting options.
    
    Args:
        limit: Maximum number of products to return
        offset: Number of products to skip (for pagination)
        sort_by: Field to sort by (rating, price, name)
        sort_order: Sort direction (asc or desc)
        brand: Filter by brand name
        category: Filter by category
    """
    try:
        # Build the query based on filters
        query = {}
        
        # Apply brand filter if specified
        if brand:
            query["brand"] = brand
            
        # Apply category filter if specified
        if category:
            # Check if we have the new schema with categories array
            # or the old schema with category field
            if db.products.find_one({"categories": {"$exists": True}}):
                query["categories"] = category
            else:
                query["category"] = category
        
        # Set up sorting
        sort_direction = -1 if sort_order.lower() == "desc" else 1
        
        # Execute the query
        products = list(
            db.products.find(query)
            .sort(sort_by, sort_direction)
            .skip(offset)
            .limit(limit)
        )
        
        # Get total count for pagination
        total_count = db.products.count_documents(query)
        
        return {
            "products": parse_json(products),
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        print(f"Error in /products: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/products/{product_id}")
def get_product_by_id(product_id: str):
    """Endpoint to get a single product by its ID."""
    try:
        product = db.products.find_one({"_id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        return parse_json(product)
    except Exception as e:
        print(f"Error in /products/{product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/search")
def search_product_catalog(
    q: str = Query(..., description="Search query"), 
    brand: Optional[str] = None,
    sort_by: str = "rating",
    limit: int = 20
):
    """
    Search the product catalog based on a query string.
    
    Args:
        q: Search query string (required)
        brand: Optional brand filter
        sort_by: Field to sort results by (default: rating)
        limit: Maximum number of results to return
    """
    try:
        # Call the search function from the recommender module
        search_results = search_products(q, brand=brand, sort_by=sort_by, limit=limit)
        
        # Return the search results and metadata
        return {
            "query": q,
            "count": len(search_results),
            "results": search_results
        }
    except Exception as e:
        print(f"Error in /search: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/brands")
def get_brands():
    """Get all available product brands."""
    try:
        brands = get_available_brands()
        return {"brands": brands}
    except Exception as e:
        print(f"Error in /brands: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/categories")
def get_categories():
    """Get all available product categories."""
    try:
        categories = get_available_categories()
        return {"categories": categories}
    except Exception as e:
        print(f"Error in /categories: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Health check endpoint
@app.get("/health")
def health_check():
    try:
        # Check DB connection
        client.admin.command('ping')
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: Cannot connect to database - {e}")

# You might want to run this using Uvicorn: 
# uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload 