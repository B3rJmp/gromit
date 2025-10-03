from app import db

class App(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  token = db.Column(db.String(100), nullable=True)
  deep_link = db.Column(db.Boolean, server_default=False)

  host_apps = db.relationship("HostApp", backref="app", lazy=True)

  def __repr__(self):
    return f"<App {self.name}>"