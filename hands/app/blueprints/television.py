import os
import time
import requests
import threading
from app import db
from app.models import User, Host, Log
from flask import abort, Blueprint

television_bp = Blueprint("television_bp", __name__)

YOUTUBE_APP_ID = os.environ.get("YOUTUBE_APP_ID", "837")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
TARGET_VOLUME = int(os.environ.get("ROKU_VOLUME", "10"))  # default volume 10

if not all([YOUTUBE_API_KEY]):
    raise ValueError("Missing required environment variables. Check your .env file.")

# Static search query
STATIC_QUERY = "lofi girl study music 24 hour"

def set_roku_volume(level: int, ip_address):
    try:
        # Push volume down more gradually with short delays
        requests.post(
            f"http://{ip_address}:8060/keydown/VolumeDown",
            timeout=5
        )

        time.sleep(5)
        requests.post(
            f"http://{ip_address}:8060/keyup/VolumeDown",
            timeout=5
        )

        time.sleep(5)

        # Push and hold volume up
        requests.post(
            f"http://{ip_address}:8060/keydown/VolumeUp",
            timeout=5
        )

        time.sleep(2.5)
        requests.post(
            f"http://{ip_address}:8060/keyup/VolumeUp",
            timeout=5
        )

        print(f"Volume set to {level}")
    except Exception as e:
        print(f"Error setting volume: {e}")


def launch_roku_video(video_id, ip_address):
    # Launch YouTube video
    launch_url = f"http://{ip_address}:8060/launch/{YOUTUBE_APP_ID}?contentID={video_id}"
    try:
        requests.post(launch_url, timeout=5)
        print(f"Video {video_id} launched on Roku")
    except Exception as e:
        print(f"Error launching video: {e}")
        return

    # Give Roku a moment to start the app
    time.sleep(5)

    # Adjust volume consistently
    set_roku_volume(TARGET_VOLUME, ip_address)


@television_bp.route("/<hostname>/start-lofi/<token>", methods=["GET"])
def start_lofi(hostname, token):
    TELEVISION = Host.query.filter_by(name=hostname).first()
    USER = User.query.filter_by(token=token).first()
    if not USER:
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

    threading.Thread(target=launch_roku_video, args=(video_id,TELEVISION.ip_address)).start()
    db.session.add(Log(user_id=USER.id,log_type_id=1,description=f"{USER.name} started lo-fi"))
    db.session.commit()
    return f"Launching: {STATIC_QUERY} ({video_id}) with volume {TARGET_VOLUME}", 200
