# recommendation-service/src/main.py
import os
import logging
from fastapi import FastAPI
from pymongo import MongoClient
from src.models.collaborative_filtering import CollaborativeFilteringModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Recommendation Service")

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://database:27017")
client = MongoClient(mongo_uri)
db = client.ecommerce

# Initialize recommendation models
cf_model = CollaborativeFilteringModel(db)

@app.on_event("startup")
async def startup_event():
    logger.info("Training recommendation models...")
    cf_model.train()
    logger.info("Models trained successfully")

@app.get("/recommendations/user/{user_id}")
async def get_user_recommendations(user_id: str, limit: int = 10):
    """Get product recommendations for a specific user"""
    recommendations = cf_model.recommend_for_user(user_id, limit)
    return {"user_id": user_id, "recommendations": recommendations}

@app.get("/recommendations/similar/{product_id}")
async def get_similar_products(product_id: str, limit: int = 10):
    """Get similar products based on a product ID"""
    similar_products = cf_model.find_similar(product_id, limit)
    return {"product_id": product_id, "similar_products": similar_products}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)