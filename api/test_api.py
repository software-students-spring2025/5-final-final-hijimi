from main import app
from unittest.mock import patch
import json
from recommender_client import recommend_popular


# Mock load_interaction_data 和 recommend_popular
@patch("main.load_interaction_data")
@patch("main.recommend_popular")
def test_recommend(mock_recommend, mock_load):
    # 模拟数据库返回数据
    mock_load.return_value = []
    mock_recommend.return_value = ["p1", "p2"]

    client = app.test_client()
    response = client.get("/recommend/u1")

    assert response.status_code == 200
    data = response.get_json()
    assert data["user_id"] == "u1"
    assert data["recommendations"] == ["p1", "p2"]


def test_recommend_popular_basic():
    df = [
        {"user_id": "u1", "product_id": "p1", "action": "purchase"},
        {"user_id": "u2", "product_id": "p1", "action": "purchase"},
        {"user_id": "u1", "product_id": "p2", "action": "click"},
    ]
    import pandas as pd

    df = pd.DataFrame(df)
    result = recommend_popular(df, "u1", top_n=1)
    assert result == ["p1"]
