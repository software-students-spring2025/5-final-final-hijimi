import os
import sys
import time
from fastapi import FastAPI, HTTPException
# Add CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import json_util
import json

# Add the recommender directory to the Python path
# This allows importing the get_recommendations function
# Adjust the path ../ based on your final structure or consider packaging the recommender
sys.path.append(os.path.join(os.path.dirname(__file__), '../recommender'))
try:
    # Attempt to import the recommendation function
    from recommender import get_recommendations, parse_json
except ImportError:
    # Provide a fallback if the recommender module isn't found or has issues
    print("Warning: Could not import get_recommendations from recommender module.")
    # Define parse_json if not imported from recommender
    def parse_json(data):
        return json.loads(json_util.dumps(data))

    def get_recommendations(user_id: str, n_recommendations: int = 5):
        print("Fallback: Recommender not available.")
        # Simple fallback: return empty list or generic popular items from DB if accessible
        try:
             # Connect to MongoDB (consider centralizing connection logic)
             MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/mydatabase') # Use service name
             client = MongoClient(MONGO_URI)
             db = client.get_database()
             popular_products = list(db.products.find().limit(n_recommendations))
             # Convert BSON ObjectId before returning from fallback
             return parse_json(popular_products) 
        except Exception as e:
             print(f"Fallback DB error: {e}")
             return []

app = FastAPI(
    title="E-commerce Recommendation API",
    description="API for serving product recommendations.",
    version="0.1.0"
)

# --- CORS Configuration ---
# Define allowed origins (where the frontend is running)
origins = [
    "http://localhost:8080",  # Frontend origin when running locally
    "http://localhost:8081",  # Frontend running on port 8081
    "http://localhost",       # Sometimes needed depending on browser/setup
    "http://157.230.224.141", # Digital Ocean Droplet IP address
    "http://ecommerce-app",   # Container name if needed
    "http://143.244.170.102:8080", # New server IP
    "*",                      # Allow all origins during development (remove in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of origins allowed to make requests
    allow_credentials=True, # Allow cookies (if needed in the future)
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)
# --- End CORS Configuration ---

# Connect to MongoDB - Support both local and cloud deployment
# The environment variable will be set in the deployment environment
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/mydatabase')

# Add retry logic for MongoDB connection
max_retries = 30
retry_interval = 2
client = None
db = None

print(f"API starting up, connecting to MongoDB at {MONGO_URI}")

for attempt in range(max_retries):
    try:
        print(f"Attempting to connect to MongoDB (attempt {attempt+1}/{max_retries})")
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
            print("Maximum retry attempts reached. API will start but some features won't work.")
            # We'll allow the API to start but endpoints that need DB access will return errors

@app.get("/")
def read_root():
    return {"message": "Welcome to the E-commerce Recommendation API"}

@app.get("/recommendations/{user_id}")
def get_user_recommendations(user_id: str, limit: int = 5):
    """Endpoint to get product recommendations for a specific user."""
    if client is None or db is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
        
    try:
        # Call the recommendation logic from the recommender module
        recommendations = get_recommendations(user_id, n_recommendations=limit)
        
        if not recommendations:
            # Handle case where no recommendations are generated (e.g., new user)
            # Return popular items as a fallback
             print(f"No specific recommendations for {user_id}, returning popular items.")
             popular_products = list(db.products.find().limit(limit))
             if not popular_products:
                  return {"user_id": user_id, "recommendations": [], "message": "No popular products found."}
             # Ensure fallback popular products are also parsed
             popular_products_json = parse_json(popular_products)
             return {"user_id": user_id, "recommendations": popular_products_json}

        # The get_recommendations function now returns parsed JSON data
        return {"user_id": user_id, "recommendations": recommendations} 

    except Exception as e:
        print(f"Error in /recommendations/{user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/products")
def get_all_products():
     """Endpoint to get a list of all products."""
     if client is None or db is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
         
     try:
         products = list(db.products.find())
         return parse_json(products)
     except Exception as e:
         print(f"Error in /products: {e}")
         raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Health check endpoint
@app.get("/health")
def health_check():
    if client is None:
        return {"status": "error", "database": "not connected"}
        
    try:
        # Check DB connection
        client.admin.command('ping')
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": f"failed: {str(e)}"}

# You might want to run this using Uvicorn: 
# uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload 