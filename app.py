import os
import time
import requests
import threading
from flask import Flask, request, abort
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Load configuration from environment variables
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN")
ROKU_IP = os.environ.get("ROKU_IP")
YOUTUBE_APP_ID = os.environ.get("YOUTUBE_APP_ID", "837")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
TARGET_VOLUME = int(os.environ.get("ROKU_VOLUME", "10"))  # default volume 10

if not all([WEBHOOK_TOKEN, ROKU_IP, YOUTUBE_API_KEY]):
    raise ValueError("Missing required environment variables. Check your .env file.")

# Static search query
STATIC_QUERY = "lofi study music 24 hour"

def set_roku_volume(level: int):
    try:
        # Push volume down more gradually with short delays
        for _ in range(50):
            requests.post(f"http://{ROKU_IP}:8060/keypress/VolumeDown", timeout=1)
            time.sleep(0.05)  # small delay to let Roku process

        # Raise to target level with delays
        for _ in range(level):
            requests.post(f"http://{ROKU_IP}:8060/keypress/VolumeUp", timeout=1)
            time.sleep(0.05)

        print(f"Volume set to {level}")
    except Exception as e:
        print(f"Error setting volume: {e}")


def launch_roku_video(video_id):
    # Launch YouTube video
    launch_url = f"http://{ROKU_IP}:8060/launch/{YOUTUBE_APP_ID}?contentID={video_id}"
    try:
        requests.post(launch_url, timeout=2)
        print(f"Video {video_id} launched on Roku")
    except Exception as e:
        print(f"Error launching video: {e}")
        return

    # Give Roku a moment to start the app
    time.sleep(3)

    # Adjust volume consistently
    set_roku_volume(TARGET_VOLUME)

@app.route("/start_lofi", methods=["GET"])
def start_lofi():
    token = request.args.get("token")
    if token != WEBHOOK_TOKEN:
        abort(403)

    # Search YouTube for the static query
    try:
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": STATIC_QUERY,
            "type": "video",
            "maxResults": 1,
            "key": YOUTUBE_API_KEY
        }
        resp = requests.get(search_url, params=params)
        resp.raise_for_status()
        items = resp.json().get("items")
        if not items:
            return "No videos found", 404
        video_id = items[0]["id"]["videoId"]
    except Exception as e:
        return f"YouTube search failed: {e}", 500

    threading.Thread(target=launch_roku_video, args=(video_id,)).start()
    return f"Launching: {STATIC_QUERY} ({video_id}) with volume {TARGET_VOLUME}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
