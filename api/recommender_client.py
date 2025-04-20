from pymongo import MongoClient
import pandas as pd


def load_interaction_data():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["ecommerce"]
    interactions = list(db["interactions"].find())
    return pd.DataFrame(interactions)


def recommend_popular(df, user_id, top_n=3):
    purchase_df = df[df["action"] == "purchase"]
    top_products = purchase_df["product_id"].value_counts().head(top_n).index.tolist()
    return top_products
