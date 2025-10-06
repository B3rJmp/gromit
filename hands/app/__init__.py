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
  app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://gromit:0IaABr00N9sZO35mMgg443SEE@brain:3306/gromit"
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  db.init_app(app)
  migrate.init_app(app, db, render_as_batch=True)

  from app.blueprints.television import television_bp
  from app.blueprints.computer import computer_bp
  from app.blueprints.light import light_bp

  app.register_blueprint(television_bp)
  app.register_blueprint(computer_bp)
  app.register_blueprint(light_bp)

  return app