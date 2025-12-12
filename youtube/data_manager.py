"""
Data manager module for handling JSON persistence of transcript cache.
"""

import json
from config import DATA_FILE_PATH


def load_data():
    """Load transcript data from JSON file."""
    try:
        with open(DATA_FILE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    """Save transcript data to JSON file."""
    with open(DATA_FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def add_transcript(data, video_id, chunks):
    """Add a new transcript to the data cache."""
    data.append({"videoId": video_id, "transcript": chunks})
    return data


def get_transcript(data, video_id):
    """Retrieve a cached transcript by video ID."""
    for item in data:
        if item["videoId"] == video_id:
            return item["transcript"]
    return None
