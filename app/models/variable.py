from app import db

class Variable(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  key = db.Column(db.String(50), nullable=False)
  value = db.Column(db.String(100), nullable=True)
  host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)

  def as_dict(self):
    return {
      "id": self.id,
      "key": self.key,
      "value": self.value,
      "host": self.host.as_dict(),
    }