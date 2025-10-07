import os
import winrm
from app.models import Host, User, Variable, Log
from app.controllers import Light
from app import db
from flask import Blueprint, jsonify, abort, request, json

computer_bp = Blueprint("computer_bp", __name__, url_prefix="/wallace")


USERNAME = os.environ.get("WALLACE_USERNAME")
PASSWORD = os.environ.get("WALLACE_PASSWORD")

@computer_bp.route("/reboot/<token>", methods=["GET"])
def reboot_windows(token):
    try:
        USER = User.query.filter_by(token=token).first()
        HAS_BOOTED = Variable.query.filter_by(key="PLEX_HAS_BOOTED").first()
        if not USER:
            abort(403)
        if not bool(HAS_BOOTED.value):
            abort(200)
        WALLACE = Host.query.filter_by(name="Wallace").first()
        WALLACE_USERNAME = Variable.query.filter_by(key="WALLACE_USERNAME").first()
        WALLACE_PASSWORD = Variable.query.filter_by(key="WALLACE_PASSWORD").first()
        session = winrm.Session(WALLACE.ip_address, auth=(WALLACE_USERNAME.value, WALLACE_PASSWORD.value))
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
    
@computer_bp.route("/plex-has-booted/<token>", methods=["PUT"])
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

@computer_bp.route("/handle-plex-event/<token>", methods=["POST"])
def handle_plex_event(token):
    try:
        USER = User.query.filter_by(token=token).first()
        if not USER or USER.name != 'Wallace':
            abort(403)
        data = json.loads(request.form['payload'])
        account = data["Account"]["title"]
        event = data["event"]
        local_player = bool(data["Player"]["local"])
        client = data["Player"]["title"]
        print(78,account,event,local_player,data["Player"])
        if account == 'B3rJmp' and local_player and (client == "Simon" or client == "Garfunkel"):
            if event == 'media.play' or event == 'media.resume':
                all_lights_off(USER)
            elif event == 'media.stop':
                kitchen_lights_on(USER)
        else:
            return "no event triggered"
    except Exception as e:
        print(e)
        return f"Error {e}"
    
def all_lights_off(user):
    db.session.add(Log(user_id=user.id,log_type_id=1,description=f"{user.name} initiated light switch"))
    hosts = Host.query.filter_by(host_type_id = 3).all()
    try:
        for host in hosts:
            USERNAME = Variable.query.filter_by(key="LIGHTS_USERNAME").first().value
            PASSWORD = Variable.query.filter_by(key="LIGHTS_PASSWORD").first().value
            try:
                light = Light(host.ip_address, USERNAME,PASSWORD)
                light.turn_off()
            except Exception as e:
                raise f"Error: {e}"
        db.session.add(Log(user_id=user.id,log_type_id=3,description=f"{user.name} switched all lights to off"))
        return f"all set to off"
    except Exception as e:
        print(23, e)
        db.session.add(Log(user_id=user.id,log_type_id=2,description=f"{user.name} failed to switched all lights to off"))
        return f"Error: {e}", 500
    
def kitchen_lights_on(user):
    db.session.add(Log(user_id=user.id,log_type_id=1,description=f"{user.name} initiated light switch"))
    hosts = Host.query.filter_by(host_type_id = 3).all()
    targetted_hosts = []
    for host in hosts:
        if host.name == 'kitchen' or host.name == 'dining':
            targetted_hosts.append(host)
    try:
        for host in targetted_hosts:
            USERNAME = Variable.query.filter_by(key="LIGHTS_USERNAME").first().value
            PASSWORD = Variable.query.filter_by(key="LIGHTS_PASSWORD").first().value
            try:
                light = Light(host.ip_address, USERNAME,PASSWORD)
                light.turn_on()
            except Exception as e:
                raise f"Error: {e}"
        db.session.add(Log(user_id=user.id,log_type_id=3,description=f"{user.name} switched kitchen lights to on"))
        return f"kitchen set to on"
    except Exception as e:
        print(23, e)
        db.session.add(Log(user_id=user.id,log_type_id=2,description=f"{user.name} failed to switched kitchen lights to on"))
        return f"Error: {e}", 500