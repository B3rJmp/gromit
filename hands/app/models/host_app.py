from app import db

class HostApp(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  host_app_name = db.Column(db.String(50), nullable=False)
  host_app_id = db.Column(db.String(50), nullable=False)
  host_id = db.Column(db.Integer, db.ForeignKey("host.id"), nullable=False)
  app_id = db.Column(db.Integer, db.ForeignKey("app.id"), nullable=True)

  def __repre__(self):
    return f"<HostApp {self.host_app_name}>"