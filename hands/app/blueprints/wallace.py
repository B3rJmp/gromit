import os
import winrm
from app.models import Host, User, Variable, Log
from app import db
from flask import Blueprint, jsonify, abort, request, json

wallace_bp = Blueprint("wallace_bp", __name__, url_prefix="/wallace")


USERNAME = os.environ.get("WALLACE_USERNAME")
PASSWORD = os.environ.get("WALLACE_PASSWORD")

@wallace_bp.route("/reboot/<token>", methods=["GET"])
def reboot_windows(token):
    try:
        USER = User.query.filter_by(token=token).first()
        HAS_BOOTED = Variable.query.filter_by(key="PLEX_HAS_BOOTED").first()
        if not USER:
            abort(403)
        if not bool(HAS_BOOTED.value):
            abort(200)
        WALLACE = Host.query.filter_by(name="Wallace").first().ip_address
        session = winrm.Session(WALLACE, auth=(USERNAME, PASSWORD))
        r = session.run_cmd("shutdown", ["/r", "/t", "0"])
        if r.status_code == 0:
            HAS_BOOTED.value = 'False'
            db.session.add(Log(user_id=USER.id,log_type_id=1,description=f"{USER.name} rebooted wallace"))
            db.session.commit()
            return jsonify({"status": "success", "message": "Windows reboot initiated"})
        else:
            db.session.add(Log(user_id=USER.id,log_type_id=2,description=f"{e}"))
            db.session.commit()
            return jsonify({
                "status": "error",
                "stdout": r.std_out.decode(),
                "stderr": r.std_err.decode()
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
@wallace_bp.route("/plex-has-booted/<token>", methods=["GET"])
def update_plex_has_booted(token):
    USER = User.query.filter_by(token=token).first()
    if not USER:
        abort(403)

    try:
        HAS_BOOTED = Variable.query.filter_by(key="PLEX_HAS_BOOTED").first()
        if not HAS_BOOTED:
            HAS_BOOTED = Variable(key="PLEX_HAS_BOOTED", value="False")
            db.session.add(HAS_BOOTED)

        HAS_BOOTED.value = 'True'
        db.session.add(Log(user_id=USER.id,log_type_id=1,description=f"{USER.name} updated Plex status to booted"))
        db.session.commit()
        return f"Plex status set to {HAS_BOOTED.value}"

    except Exception as e:
        db.session.rollback()
        db.session.add(Log(user_id=USER.id,log_type_id=2,description=f"{e}"))
        db.session.commit()
        print(f"Error setting PLEX_HAS_BOOTED: {e}")
        return f"Internal error: {e}", 500

@wallace_bp.route("/handle-plex-event/<token>", methods=["POST"])
def handle_plex_event(token):
    try:
        USER = User.query.filter_by(token=token).first()
        if not USER or USER.name != 'Wallace':
            abort(403)
        data = json.loads(request.form['payload'])
        account = data["Account"]["title"]
        event = data["event"]
        local_player = bool(data["Player"]["local"])
        if (account == 'Simon' and (event == 'media.play' or event == 'media.resume') and local_player):
            #lights on
            return 'event triggered'
        else:
            return "no event triggered"
    except Exception as e:
        print(e)
        return f"Error {e}"
