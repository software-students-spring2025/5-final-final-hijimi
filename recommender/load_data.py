from pymongo import MongoClient
import pandas as pd

def load_interaction_data():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["ecommerce"]
    interactions = list(db["interactions"].find())
    return pd.DataFrame(interactions)
