"""MongoDB helpers for storing and retrieving gesture results."""

import os

from pymongo import MongoClient

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)
db = client["rps_game"]
gestures_collection = db["gestures"]


def save_result(image_bytes, gesture, created_at):
    """Save a gesture result to MongoDB."""
    doc = {
        "image": image_bytes,
        "gesture": gesture,
        "created_at": created_at,
    }
    result = gestures_collection.insert_one(doc)
    print(f"Saved {gesture} at {created_at}")
    return result.inserted_id


def get_latest_result():
    """Return the most recent gesture result."""
    doc = gestures_collection.find_one(sort=[("created_at", -1)])

    if doc is None:
        return None

    return {
        "gesture": doc.get("gesture"),
        "created_at": doc.get("created_at"),
    }