import os
import time
import requests
import unicodedata
import xml.etree.ElementTree as ET
import threading
from app import db
from app.models import *
from flask import abort, Blueprint, request, jsonify

television_bp = Blueprint("television_bp", __name__)

def set_roku_volume(ip_address):
    try:
        # Push volume down more gradually with short delays
        requests.post(
            f"http://{ip_address}:8060/keydown/VolumeDown",
            timeout=5
        )

        time.sleep(7)
        requests.post(
            f"http://{ip_address}:8060/keyup/VolumeDown",
            timeout=5
        )

        time.sleep(3)

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
    except Exception as e:
        print(f"Error setting volume: {e}")


def launch_roku_video(video_id, ip_address, app_id):
    # Launch YouTube video
    launch_url = f"http://{ip_address}:8060/launch/{app_id}?contentID={video_id}"
    try:
        requests.post(launch_url, timeout=5)
        print(f"Video {video_id} launched on Roku")
    except Exception as e:
        print(f"Error launching video: {e}")
        return

    # Give Roku a moment to start the app
    time.sleep(5)

    # Adjust volume consistently
    set_roku_volume(ip_address)


@television_bp.route("/<host_name>/start-lofi/<token>", methods=["GET"])
def start_lofi(host_name, token):
    HOST = Host.query.filter_by(name=host_name).first()
    USER = User.query.filter_by(token=token).first()
    if not USER:
        abort(403)
    YOUTUBE_APP_ID = HostApp.query.filter_by(host_app_name="youtube").first().host_app_id
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

    if not all([YOUTUBE_API_KEY]):
        raise ValueError("Missing required environment variables. Check your .env file.")

    # Static search query
    STATIC_QUERY = "lofi girl music"

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

    threading.Thread(target=launch_roku_video, args=(video_id,HOST.ip_address,YOUTUBE_APP_ID)).start()
    db.session.add(Log(user_id=USER.id,log_type_id=1,description=f"{USER.name} started lo-fi"))
    db.session.commit()
    return f"Launching: {STATIC_QUERY} ({video_id})", 200

@television_bp.route("/launch/<app_name>/<host_name>/<token>")
def launch_app(app_name, host_name, token):
    USER = User.query.filter_by(token=token).first()
    if not USER:
        abort(403)
    HOST = Host.query.filter_by(name=host_name).first()
    if not HOST:
        abort(404)
    APP = App.query.filter_by(name=app_name).first()
    if not APP:
        db.session.add(App(name=app_name))
        db.session.commit()
        APP = App.query.filter_by(name=app_name).first()
    HOST_APPS = HostApp.query.filter_by(host_id=HOST.id).all()
    if not HOST_APPS:
        try:
            apps = query_host_for_apps(HOST)
            for app in apps:
                db.session.add(HostApp(host_app_name=app["app_name"], host_app_id=app["app_id"], host_id=HOST.id))
            db.session.commit()
            HOST_APPS = HostApp.query.filter_by(host_id=HOST.id).all()
        except Exception as e:
            return f"Error: {e}"
        
    MATCHED_HOST_APP = next((app for app in HOST_APPS if app.app_id and app.app_id == APP.id), None)
    if not MATCHED_HOST_APP:
        try:
            MATCHED_HOST_APP = try_to_find_host_app(HOST_APPS, APP)
            if not MATCHED_HOST_APP:
                raise TypeError("No app was able to be matched")
            MATCHED_HOST_APP.app_id = APP.id
            db.session.add(MATCHED_HOST_APP)
            db.session.commit()
        except Exception as e:
            return f"Error: {e}"
    QUERY = request.args.get('query') if request.args.get('query') else None
    
    if QUERY:
        content_id = handle_content_query(QUERY, app_name)
    else:
        content_id = None
    

    base_url = f"http://{HOST.ip_address}"
    if HOST.port_number:
        base_url += f":{HOST.port_number}"
    launch_path = f"/launch/{MATCHED_HOST_APP.host_app_id}"
    content_id_arg = f"?contentId={content_id}" if content_id else ""
    launch_url = base_url + launch_path + content_id_arg
    try:
        requests.post(launch_url, timeout=5)
        print(f"{app_name} launched on {HOST.name}")
        return f"{app_name} launched on {HOST.name}", 200
    except Exception as e:
        return f"Error: {e}", 500

def query_host_for_apps(host):
    import requests
    import xml.etree.ElementTree as ET

    # Build the query URL
    if host.port_number and host.port_number != "80":
        url = f"http://{host.ip_address}:{host.port_number}/query/apps"
    else:
        url = f"http://{host.ip_address}/query/apps"
        
    resp = requests.get(url)
    resp.raise_for_status()

    # Parse XML
    root = ET.fromstring(resp.text)
    apps = []
    for app in root.findall("app"):
        app_text = app.text.strip().lower()
        app_id = app.attrib["id"]
        apps.append({"app_name": app_text, "app_id": app_id})
    return apps

def normalize_app_name(name):
    # Convert to lowercase
    name = name.lower()
    # Remove dashes, underscores, plus
    for ch in "-_+":
        name = name.replace(ch, "")
    # Normalize Unicode, remove all whitespace
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not c.isspace())
    return name

def try_to_find_host_app(apps, target_app):
    
    formatted_name = normalize_app_name(target_app.name)

    for app in apps:
        app_name = app.host_app_name.strip()
        print(193,normalize_app_name(app.host_app_name.strip()))
        print(194,formatted_name)
        print(195,normalize_app_name(app.host_app_name.strip()).find(formatted_name))
        if normalize_app_name(app_name).find(formatted_name) != -1:
            return app
    return None

    
def handle_content_query(query, app_name):
    return 'blah'
