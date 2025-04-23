from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from client import call_recommender

class UserIn(BaseModel):
    user_id: int

app = FastAPI()

@app.post("/v1/recommend")
async def recommend(user: UserIn):
    try:
        return await call_recommender(user.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
