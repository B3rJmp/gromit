from flask import abort, Blueprint, request, jsonify
from app.controllers import Light
from app.models import Host, Variable

light_bp = Blueprint("light_bp", __name__, url_prefix="/light")

@light_bp.route("/<location>/<state>", methods=["GET"])
def hand_single_light(location, state):
  host = Host.query.filter_by(name=location).first()
  try:
    control_light(host.ip_address, state)
    return f"{location} set to {state}"
  except Exception as e:
    return f"Error: {e}", 500
  
@light_bp.route("/all/<state>", methods=["GET"])
def handle_all_lights(state):
  hosts = Host.query.filter_by(host_type_id=3).all()
  for host in hosts:
    control_light(host.ip_address, state)
  return f"all lights set to {state}"

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