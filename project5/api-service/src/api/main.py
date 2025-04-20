# api-service/src/api/main.py
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import httpx
from src.api.auth import get_current_user
from src.api.routes import products, users, cart
from src.models.user import User

# Initialize FastAPI app
app = FastAPI(title="E-commerce API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://database:27017")
client = MongoClient(mongo_uri)
db = client.ecommerce

# Recommendation service URL
rec_service_url = os.getenv("REC_SERVICE_URL", "http://recommendation-service:8000")

# Include routers
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])

@app.get("/")
async def root():
    return {"message": "E-commerce API is running"}

@app.get("/recommendations/personalized", tags=["recommendations"])
async def get_personalized_recommendations(current_user: User = Depends(get_current_user)):
    """Get personalized recommendations for the authenticated user"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{rec_service_url}/recommendations/user/{current_user.id}",
                params={"limit": 10}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error fetching recommendations"
                )
                
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

@app.get("/recommendations/similar/{product_id}", tags=["recommendations"])
async def get_similar_products(product_id: str):
    """Get similar products based on a product ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{rec_service_url}/recommendations/similar/{product_id}",
                params={"limit": 10}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error fetching similar products"
                )
                
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )