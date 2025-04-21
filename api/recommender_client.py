from pymongo import MongoClient
import pandas as pd


def load_interaction_data():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["ecommerce"]
    interactions = list(db["interactions"].find())
    return pd.DataFrame(interactions)


def recommend_popular(df, user_id, top_n=5):
    seen_products = df[df["user_id"] == user_id]["product_id"].tolist()
    popular = (
        df[~df["product_id"].isin(seen_products)]
        .groupby("product_id")
        .size()
        .sort_values(ascending=False)
        .head(top_n)
        .index.tolist()
    )
    return popular
