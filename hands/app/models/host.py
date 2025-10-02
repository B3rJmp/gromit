from app import db

class Host(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  ip_address = db.Column(db.String(50), nullable=False)
  port_number = db.Column(db.String(50), nullable=True)
  host_type_id = db.Column(db.Integer, db.ForeignKey('host_type.id'), nullable=True)

  variables = db.relationship('Variable', backref='host', lazy=True)

  def __repr__(self):
    return f"<Host {self.name}>"
