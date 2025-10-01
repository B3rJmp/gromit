import os
import winrm
from app.models import Host, User, Variable
from app import db
from flask import Blueprint, jsonify, abort

wallace_bp = Blueprint("wallace_bp", __name__, url_prefix="/wallace")

@wallace_bp.route("/reboot/<token>", methods=["GET"])
def reboot_windows(token):
    try:
        USER = User.query.filter_by(token=token).first()
        HAS_BOOTED = Variable.query.filter_by(key="PLEX_HAS_BOOTED").first()
        if not USER:
            abort(403)
        if not bool(HAS_BOOTED.value):
            abort(200)
        USERNAME = Variable.query.filter_by(key="WALLACE_USERNAME").first().value
        PASSWORD = Variable.query.filter_by(key="WALLACE_PASSWORD").first().value
        WALLACE = Host.query.filter_by(name="Wallace").first().ip_address
        session = winrm.Session(WALLACE, auth=(USERNAME, PASSWORD))
        r = session.run_cmd("shutdown", ["/r", "/t", "0"])
        if r.status_code == 0:
            HAS_BOOTED.value = 'False'
            db.session.commit()
            return jsonify({"status": "success", "message": "Windows reboot initiated"})
        else:
            return jsonify({
                "status": "error",
                "stdout": r.std_out.decode(),
                "stderr": r.std_err.decode()
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
@wallace_bp.route("/plex-has-booted/<token>", methods=["GET", "POST"])
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
        db.session.commit()
        return f"Plex status set to {HAS_BOOTED.value}"

    except Exception as e:
        db.session.rollback()
        print(f"Error setting PLEX_HAS_BOOTED: {e}")
        return f"Internal error: {e}", 500
