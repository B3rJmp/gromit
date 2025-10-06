from flask import abort, Blueprint, request, jsonify
from app.controllers import Light
from app.models import User, Host, Variable, Log

light_bp = Blueprint("light_bp", __name__, url_prefix="/light")

@light_bp.route("/<location>/<state>/<token>", methods=["GET"])
def handle_light(location, state, token):
  USER = User.query.filter_by(token = token).first()
  if not USER:
    abort(403)
  if(location == 'all'):
    hosts = Host.query.filter_by(host_type_id = 3).all()
  else:
    hosts = [Host.query.filter_by(name=location).first()]
  try:
    for host in hosts:
      control_light(host.ip_address, state)
    return f"{location} set to {state}"
  except Exception as e:
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