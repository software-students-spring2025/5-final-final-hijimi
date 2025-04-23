from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from models import RecRequest, RecResponse
from services import make_recommendations
import os

app = FastAPI()
client = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client["ecomm"]

@app.post("/recommend", response_model=RecResponse)
async def recommend(req: RecRequest):
    user = db.users.find_one({"_id": req.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recs = make_recommendations(user["preference"])
    return RecResponse(items=recs)
