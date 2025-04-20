from model import recommend_popular
import pandas as pd

def test_recommend_popular():
    df = pd.DataFrame([
        {"user_id": "u1", "product_id": "p1", "action": "purchase"},
        {"user_id": "u2", "product_id": "p1", "action": "purchase"},
        {"user_id": "u2", "product_id": "p2", "action": "purchase"},
    ])
    result = recommend_popular(df, "u1", top_n=1)
    assert result == ["p1"]
