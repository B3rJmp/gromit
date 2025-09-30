from app import db

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  token = db.Column(db.String(100), nullable=False)

  def __repr__(self):
    return f'<User {self.name}>'
  
  def as_dict(self):
    return {
      "id": self.id,
      "name": self.name,
      "token": self.token,
    }