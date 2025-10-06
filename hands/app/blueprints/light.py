from flask import abort, Blueprint, request, jsonify
from app import db
from app.controllers import Light
from app.models import User, Host, Variable, Log

light_bp = Blueprint("light_bp", __name__, url_prefix="/light")

@light_bp.route("/<location>/<state>/<token>", methods=["GET"])
def handle_light(location, state, token):
  USER = User.query.filter_by(token = token).first()
  if not USER:
    abort(403)
  db.session.add(Log(user_id=USER.id,log_type_id=1,description=f"{USER.name} initiated light switch"))
  if(location == 'all'):
    hosts = Host.query.filter_by(host_type_id = 3).all()
  else:
    hosts = [Host.query.filter_by(name=location).first()]
  try:
    for host in hosts:
      control_light(host.ip_address, state)
    db.session.add(Log(user_id=USER.id,log_type_id=3,description=f"{USER.name} switched {location} lights to {state}"))
    return f"{location} set to {state}"
  except Exception as e:
    print(23, e)
    db.session.add(Log(user_id=USER.id,log_type_id=2,description=f"{USER.name} failed to switched {location} lights to {state}"))
    return f"Error: {e}", 500

def control_light(ip_address, state):
  USERNAME = Variable.query.filter_by(key="LIGHTS_USERNAME").first().value
  PASSWORD = Variable.query.filter_by(key="LIGHTS_PASSWORD").first().value
  try:
    light = Light(ip_address, USERNAME,PASSWORD)
    if state == "on":
      light.turn_on()
    elif state == "off":
      light.turn_off()
    else:
      light.toggle()
  except Exception as e:
    raise f"Error: {e}"