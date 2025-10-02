from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv() 
db = SQLAlchemy()
migrate = Migrate()

def create_app():
  # Load environment variables from .env 
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  db.init_app(app)
  migrate.init_app(app, db)

  from app.blueprints.simon import simon_bp
  from app.blueprints.wallace import wallace_bp

  app.register_blueprint(simon_bp)
  app.register_blueprint(wallace_bp)

  return app