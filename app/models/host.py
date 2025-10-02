from app import db

class Host(db.Model):
  __tablename__ = "host"
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  ip_address = db.Column(db.String(50), nullable=True)

  variables = db.relationship('Variable', backref='host', lazy=True)

  def __repr__(self):
    return f"<Host {self.name}>"
