import requests
from flask import abort, Blueprint
from app import db
from app.models import User, Host, Log

garage_bp = Blueprint("garage_bp", __name__, url_prefix="/garage")

@garage_bp.route("/open/<token>", methods=["GET"])
def handle_light(token):
  USER = User.query.filter_by(token = token).first()
  if not USER:
    abort(403)
  db.session.add(Log(user_id=USER.id,log_type_id="1",description=f"{USER.name} initiated the garage"))
  GARAGE = Host.query.filter_by(name="garage").first()
  try:
    url = f"http://{GARAGE.ip_address}/relay/0?turn=toggle"
    resp = requests.get(url)
    db.session.add(Log(user_id=USER.id,log_type_id="3",description=f"{USER.name} toggled the garage"))
    db.session.commit()
    return "Garage was opened"
  except Exception as e:
    db.session.add(Log(user_id=USER.id,log_type_id="2",description=f"{USER.name} failed to activate the garage"))
    db.session.commit()
    return f"Error: {e}"
  