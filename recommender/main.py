# main.py
from load_data import load_interaction_data
from model import recommend_by_user_history

if __name__ == "__main__":
    df = load_interaction_data()
    user_id = "u1"
    recommendations = recommend_by_user_history(df, user_id)
    print("Recommended products for u1:", recommendations)
