from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():

    # Load environment variables from .env
    app = Flask(__name__)

    from app.blueprints.simon import simon_bp
    # from blueprints.wallace import wallace_bp

    app.register_blueprint(simon_bp)

    return app
