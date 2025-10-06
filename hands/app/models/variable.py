from app import db

class Variable(db.Model):  
  id = db.Column(db.Integer, primary_key=True)
  key = db.Column(db.String(50), nullable=False)
  value = db.Column(db.String(100), nullable=True)
  host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=True)

  def __repr__(self):
    return f"<Variable {self.key}>"