import pandas as pd
from model import recommend_popular
from load_data import load_interaction_data


def test_recommend_popular():
    df = pd.DataFrame(
        [
            {"user_id": "u1", "product_id": "p1", "action": "purchase"},
            {"user_id": "u2", "product_id": "p1", "action": "purchase"},
            {"user_id": "u2", "product_id": "p2", "action": "purchase"},
        ]
    )
    result = recommend_popular(df, "u1", top_n=1)
    assert result == ["p1"]


def test_main_recommend_call():
    df = pd.DataFrame(
        [
            {"user_id": "u1", "product_id": "p1", "action": "purchase"},
            {"user_id": "u1", "product_id": "p2", "action": "purchase"},
        ]
    )
    result = recommend_popular(df, "u1", top_n=2)
    assert set(result) == {"p1", "p2"}


def test_load_interaction_data(monkeypatch):
    class FakeCollection:
        def find(self):
            return [
                {"user_id": "u1", "product_id": "p1", "action": "purchase"},
                {"user_id": "u2", "product_id": "p2", "action": "view"},
            ]

    class FakeDB:
        def __getitem__(self, name):
            return FakeCollection()

    class FakeClient:
        def __getitem__(self, name):
            return FakeDB()

    monkeypatch.setattr("load_data.MongoClient", lambda *args, **kwargs: FakeClient())
    df = load_interaction_data()
    assert df.shape[0] == 2
    assert "user_id" in df.columns
