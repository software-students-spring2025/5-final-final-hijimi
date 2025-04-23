from pymongo import MongoClient
import pandas as pd


def load_interaction_data():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["ecommerce"]
    interactions = list(db["interactions"].find())
    return pd.DataFrame(interactions)


def recommend_by_user_history(df, user_id):
    seen_products = df[df["user_id"] == user_id]["product_id"].tolist()
    if not seen_products:
        return []
    popular = (
        df[~df["product_id"].isin(seen_products)]
        .groupby("product_id")
        .size()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )
    return popular
