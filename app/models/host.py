from app import db

class Host(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  ip_address = db.Column(db.String(50), nullable=True)

  variables = db.relationship('Variable', backref='host', lazy=True)

  def as_dict(self):
    return {
      "id": self.id,
      "name": self.name,
      "ip_address": self.ip_address
    }
