from app import db

class HostType(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(50), nullable=False)

  hosts = db.relationship("Host", backref="host_type", lazy=True)

  def __repr__(self):
    return f"<HostType {self.name}>"
