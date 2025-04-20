from flask import Flask, jsonify
from recommender_client import load_interaction_data, recommend_popular

app = Flask(__name__)


@app.route("/recommend/<user_id>", methods=["GET"])
def recommend(user_id):
    df = load_interaction_data()
    recommendations = recommend_popular(df, user_id)
    return jsonify({"user_id": user_id, "recommendations": recommendations})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
