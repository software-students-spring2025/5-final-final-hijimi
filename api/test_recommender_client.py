import sys
import os
import pandas as pd

# 添加项目根目录到模块路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from recommender_client import recommend_by_user_history


def test_recommend_by_user_history_basic():
    df = pd.DataFrame(
        [
            {"user_id": "u1", "product_id": "p1", "action": "purchase"},
            {"user_id": "u2", "product_id": "p2", "action": "click"},
            {"user_id": "u3", "product_id": "p2", "action": "click"},
            {"user_id": "u4", "product_id": "p3", "action": "click"},
        ]
    )
    result = recommend_by_user_history(df, "u1")
    assert "p2" in result or "p3" in result
    assert "p1" not in result
