def recommend_by_user_history(df, user_id):
    """
    简单的基于用户历史的推荐逻辑：
    如果该用户存在，则推荐该用户曾经看过的最后两个商品。
    如果该用户不存在，则返回热门商品（如 p1, p2）。
    """
    if user_id in df["user_id"].values:
        user_df = df[df["user_id"] == user_id]
        last_products = user_df["product_id"].tail(2).tolist()
        return last_products
    else:
        return ["p1", "p2"]  # 热门商品作为默认推荐
