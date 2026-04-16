import os
import base64
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongodb:27017/mydb")
client = MongoClient(MONGO_URI)
db = client.get_default_database()
results_collection = db["results"]


def serialize_result(doc):
    image_b64 = None
    if doc.get("image"):
        image_b64 = base64.b64encode(doc["image"]).decode("utf-8")

    timestamp = doc.get("timestamp")
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    elif isinstance(timestamp, datetime):
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        timestamp_str = str(timestamp)

    return {
        "id": str(doc["_id"]),
        "gesture": doc.get("gesture", "unknown"),
        "timestamp": timestamp_str,
        "image": image_b64,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/results")
def get_results():
    docs = list(results_collection.find().sort("_id", -1).limit(20))
    return jsonify([serialize_result(d) for d in docs])


@app.route("/api/stats")
def get_stats():
    pipeline = [{"$group": {"_id": "$gesture", "count": {"$sum": 1}}}]
    raw = list(results_collection.aggregate(pipeline))
    stats = {item["_id"]: item["count"] for item in raw}
    total = sum(stats.values())
    return jsonify({
        "rock": stats.get("rock", 0),
        "paper": stats.get("paper", 0),
        "scissors": stats.get("scissors", 0),
        "total": total,
    })


@app.route("/api/latest")
def get_latest():
    doc = results_collection.find_one(sort=[("_id", -1)])
    if doc is None:
        return jsonify(None)
    return jsonify(serialize_result(doc))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)