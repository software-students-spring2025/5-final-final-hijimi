from pydantic import BaseModel
from typing import List

class RecRequest(BaseModel):
    user_id: int

class RecResponse(BaseModel):
    items: List[str]
