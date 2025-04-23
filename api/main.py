from flask import Flask, jsonify
from flask_cors import CORS
from recommender_client import load_interaction_data, recommend_by_user_history

app = Flask(__name__)
CORS(app)


@app.route("/recommend/<user_id>", methods=["GET"])
def recommend(user_id):
    try:
        df = load_interaction_data()
        if user_id not in df["user_id"].values:
            return (
                jsonify(
                    {
                        "user_id": user_id,
                        "recommendations": [],
                        "message": "No history found for this user.",
                    }
                ),
                200,
            )
        recommendations = recommend_by_user_history(df, user_id)
        return jsonify({"user_id": user_id, "recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
