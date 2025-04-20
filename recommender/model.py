def recommend_popular(df, user_id, top_n=3):
    """
    推荐最受欢迎的商品（购买次数最多）
    """
    purchase_df = df[df["action"] == "purchase"]
    top_products = purchase_df["product_id"].value_counts().head(top_n).index.tolist()
    return top_products
