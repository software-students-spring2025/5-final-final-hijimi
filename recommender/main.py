from load_data import load_interaction_data
from model import recommend_popular

if __name__ == "__main__":
    df = load_interaction_data()
    recommendations = recommend_popular(df, user_id="u1")
    print("Recommended products for u1:", recommendations)
