from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
app = Flask(__name__)

from blueprints.simon import simon_bp
# from blueprints.wallace import wallace_bp

app.register_blueprint(simon_bp)
# app.register_blueprint(wallace_bp)


# Load configuration from environment variables


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
