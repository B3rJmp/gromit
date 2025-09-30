import os
import shlex
import subprocess
import threading
from datetime import datetime
from flask import Blueprint, request, abort

wallace_bp = Blueprint("wallace_bp", __name__, url_prefix="/wallace")

WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN")
PSEXEC_PATH = os.environ.get("PSEXEC_PATH")  # e.g. /home/pi/impacket/examples/psexec.py
LOGFILE = os.environ.get("LOGFILE", "/tmp/reboot-server.log")

def log_msg(msg: str):
    ts = datetime.utcnow().isoformat()
    with open(LOGFILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def run_psexec_shutdown(domain_user: str, password: str, target_ip: str):
    """
    Runs impacket/examples/psexec.py to execute a forced reboot.
    domain_user should be either 'DOMAIN/Username' or just 'Username'.
    password is the user's password.
    """
    # Build credential string expected by psexec: USER:PASS@HOST
    # If a domain is needed, include it in domain_user (e.g. WORKGROUP/Administrator)
    cred = f"{domain_user}:{password}@{target_ip}"

    # Command: python3 psexec.py <cred> "shutdown /r /t 0 /f"
    cmd = [
        "python3",
        PSEXEC_PATH,
        cred,
        "shutdown /r /t 0 /f"
    ]

    safe_cmd_str = " ".join(shlex.quote(p) for p in cmd)
    log_msg(f"Executing: {safe_cmd_str}")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        log_msg(f"Return code: {proc.returncode}")
        if proc.stdout:
            log_msg(f"STDOUT: {proc.stdout.strip()}")
        if proc.stderr:
            log_msg(f"STDERR: {proc.stderr.strip()}")
    except subprocess.TimeoutExpired:
        log_msg("psexec timed out")
    except Exception as e:
        log_msg(f"Exception running psexec: {e}")

@wallace_bp.route("/reboot", methods=["POST"])
def reboot_server():
    """
    POST body must be JSON:
    {
      "user": "WORKGROUP/Administrator",   # or "Administrator"
      "password": "P@ssw0rd",
      "target": "192.168.1.2"
    }
    Query param: ?token=YOUR_TOKEN or include token in JSON as "token".
    """
    token = request.args.get("token") or (request.json or {}).get("token")
    if token != WEBHOOK_TOKEN:
        abort(403)

    data = request.get_json(force=True, silent=True)
    if not data:
        return "Expected JSON body", 400

    user = data.get("user")
    password = data.get("password")
    target = data.get("target")
    if not all([user, password, target]):
        return "Missing user/password/target in JSON body", 400

    # run in background
    threading.Thread(target=run_psexec_shutdown, args=(user, password, target), daemon=True).start()

    log_msg(f"Received reboot request for {target} by {user}")
    return ("Accepted: reboot scheduled", 202)